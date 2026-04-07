from backend.services.evaluation_service import EvaluationService


class TopicTrainingService:
    def __init__(self, *, model_manager, multi_model_service, sqlite_memory, judge_service):
        self.model_manager = model_manager
        self.multi_model_service = multi_model_service
        self.sqlite_memory = sqlite_memory
        self.judge_service = judge_service
        self.evaluator = EvaluationService()

    def enqueue_topic(self, *, message: str, task_queue):
        topic = self._extract_topic(message)
        subtopics = self._subtopics(topic)
        topic_id = self.sqlite_memory.create_training_topic(topic=topic, subtopics=subtopics)
        task_queue.enqueue(
            "topic_training",
            payload={"topic_id": topic_id, "topic": topic, "subtopics": subtopics},
            source="user_training_command",
            priority=3,
        )
        return {
            "topic_id": topic_id,
            "topic": topic,
            "subtopics": subtopics,
        }

    def process_topic_job(self, job: dict):
        payload = job.get("payload", {})
        topic_id = int(payload["topic_id"])
        topic = payload["topic"]
        subtopics = payload["subtopics"]
        completed = []
        results = []

        self.sqlite_memory.update_training_topic(topic_id=topic_id, status="running")

        for subtopic in subtopics:
            candidates = self.model_manager.choose_candidates("training")
            prompt = self._build_prompt(topic, subtopic)
            comparisons = self.multi_model_service.compare(prompt=prompt, models=candidates[:3])
            best = self._choose_best(prompt, comparisons)
            if best is None:
                continue

            completed.append(subtopic)
            self.sqlite_memory.store_topic_knowledge(
                topic_id=topic_id,
                topic=topic,
                subtopic=subtopic,
                model=best["model"],
                answer=best["response"],
                score=best["score"],
            )
            self.sqlite_memory.record_model_decision(
                task_type="training",
                selected_model=best["model"],
                candidates=candidates[:3],
                status="ok",
                judge_method=best.get("judge_method", ""),
                judge_score=best.get("judge_score"),
            )
            results.append(best)
            self.sqlite_memory.update_training_topic(
                topic_id=topic_id,
                status="running",
                completed_subtopics=completed,
            )

        self.sqlite_memory.update_training_topic(
            topic_id=topic_id,
            status="completed",
            completed_subtopics=completed,
        )
        return {
            "topic_id": topic_id,
            "topic": topic,
            "subtopics_completed": completed,
            "results": results,
        }

    def _extract_topic(self, message: str):
        lowered = message.strip()
        for prefix in ["Train yourself on:", "train yourself on:", "Train on:", "train on:"]:
            if lowered.startswith(prefix):
                return lowered[len(prefix):].strip()
        return lowered

    def _subtopics(self, topic: str):
        normalized = topic.strip()
        return [
            f"{normalized} fundamentals",
            f"{normalized} examples",
            f"{normalized} common mistakes",
            f"{normalized} best practices",
        ]

    def _build_prompt(self, topic: str, subtopic: str):
        return f"""
Teach an assistant about this topic with a concise but useful explanation.

Topic: {topic}
Subtopic: {subtopic}

Return a practical answer that can be stored as internal learning material.
"""

    def _choose_best(self, prompt: str, comparisons: list[dict]):
        ranked = self.judge_service.rank_candidates(
            prompt=prompt,
            candidates=comparisons,
            task_type="training",
        )
        if not ranked:
            return None

        best = ranked[0]
        return {
            "model": best["model"],
            "response": best["response"],
            "score": best["judge_score"],
            "evaluation": best.get("evaluation", {}),
            "judge_method": best.get("judge_method", ""),
            "judge_notes": best.get("judge_notes", []),
        }
