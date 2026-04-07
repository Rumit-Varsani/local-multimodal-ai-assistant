from backend.services.brain_state_service import BrainStateService
from backend.services.evaluation_service import EvaluationService
from backend.services.interaction_log_service import InteractionLogService
from backend.services.llm_service import LLMService, LLMServiceError
from backend.services.message_parser_service import MessageParserService
from backend.services.planner_service import PlannerService
from backend.services.reflection_service import ReflectionService
from backend.runtime import model_manager, multi_model_service, sqlite_memory
from backend.agents.memory_agent import MemoryAgent


class ChatAgent:
    def __init__(self):
        self.llm = LLMService()
        self.memory = MemoryAgent()
        self.brain_state = BrainStateService()
        self.interaction_log = InteractionLogService()
        self.message_parser = MessageParserService()
        self.reflection_service = ReflectionService()
        self.planner = PlannerService()
        self.evaluator = EvaluationService()

    def run(self, message: str):
        if not message:
            return "Please provide a message."

        parsed_messages = self.message_parser.parse(message)
        if len(parsed_messages) > 1:
            responses = []
            for item in parsed_messages:
                responses.append(self._run_single(item))
            return "\n".join(responses)

        return self._run_single(message)

    def _run_single(self, message: str):
        self.brain_state.increment_metric("total_interactions")

        try:
            memory_context = self.memory.get_context(message)
            context_block = memory_context if memory_context else "No relevant memory."
        except Exception as e:
            print("❌ Memory error:", e)
            context_block = "No relevant memory."

        plan = self.planner.plan(
            message=message,
            preferences=self.brain_state.get_preferences(),
            memory_hit=context_block != "No relevant memory.",
        )

        direct_memory_answer = self.memory.answer_personal_question(message)
        if direct_memory_answer is not None:
            self.brain_state.increment_metric("memory_hits")
            evaluation = self.evaluator.evaluate(
                user_message=message,
                assistant_response=direct_memory_answer,
                status="memory_recall",
                plan=plan,
            )
            self._log_interaction(
                user_message=message,
                assistant_response=direct_memory_answer,
                memory_context="Direct personal memory lookup.",
                status="memory_recall",
                plan=plan,
                evaluation=evaluation,
            )
            self._store_lessons(
                user_message=message,
                assistant_response=direct_memory_answer,
                status="memory_recall",
                plan=plan,
                evaluation=evaluation,
            )
            self.brain_state.record_evaluation(evaluation)
            return direct_memory_answer

        preference_update_answer = self.memory.answer_preference_update(message)
        if preference_update_answer is not None:
            try:
                self.memory.store_interaction(message, preference_update_answer)
            except Exception as e:
                print("❌ Memory store error:", e)

            self.brain_state.increment_metric("preference_updates")
            evaluation = self.evaluator.evaluate(
                user_message=message,
                assistant_response=preference_update_answer,
                status="preference_update",
                plan=plan,
            )
            self._log_interaction(
                user_message=message,
                assistant_response=preference_update_answer,
                memory_context="Direct preference update.",
                status="preference_update",
                plan=plan,
                evaluation=evaluation,
            )
            self._store_lessons(
                user_message=message,
                assistant_response=preference_update_answer,
                status="preference_update",
                plan=plan,
                evaluation=evaluation,
            )
            self.brain_state.record_evaluation(evaluation)
            return preference_update_answer

        fact_update_answer = self.memory.answer_fact_update(message)
        if fact_update_answer is not None:
            try:
                self.memory.store_interaction(message, fact_update_answer)
            except Exception as e:
                print("❌ Memory store error:", e)

            evaluation = self.evaluator.evaluate(
                user_message=message,
                assistant_response=fact_update_answer,
                status="fact_update",
                plan=plan,
            )
            self._log_interaction(
                user_message=message,
                assistant_response=fact_update_answer,
                memory_context="Direct fact update.",
                status="fact_update",
                plan=plan,
                evaluation=evaluation,
            )
            self._store_lessons(
                user_message=message,
                assistant_response=fact_update_answer,
                status="fact_update",
                plan=plan,
                evaluation=evaluation,
            )
            self.brain_state.record_evaluation(evaluation)
            return fact_update_answer

        print("🧠 MEMORY:", context_block)

        try:
            lessons = self.brain_state.find_relevant_lessons(message)
            lesson_block = self._format_lessons(lessons)
        except Exception as e:
            print("❌ Lesson error:", e)
            lesson_block = "No relevant lessons."

        try:
            style_instruction = self.memory.get_response_style_instruction()
        except Exception as e:
            print("❌ Preference error:", e)
            style_instruction = "No saved response style preference."

        brain_snapshot = self._format_brain_snapshot()

        # -----------------------------
        # 2. BUILD PROMPT
        # -----------------------------
        full_prompt = f"""
You are a helpful AI assistant.

Rules:
- Answer naturally and concisely
- Do NOT mention you are an AI
- Keep responses short and clear
- If unsure, say: "I don't have that information."
- Follow the planning strategy for this message.

Plan:
Intent: {plan['intent']}
Strategy: {plan['strategy']}
Response Style: {plan['response_style']}
Response Modes: {", ".join(plan['response_modes']) if plan['response_modes'] else "none"}

Memory:
{context_block}

Lessons:
{lesson_block}

Brain:
{brain_snapshot}

Style Preference:
{style_instruction}

User:
{message}

Assistant:
"""

        # -----------------------------
        # 3. LLM CALL
        # -----------------------------
        try:
            candidates = model_manager.choose_candidates(plan["intent"] if plan["intent"] in {"code_generation"} else "general_chat")
            model_result = multi_model_service.generate(prompt=full_prompt, models=candidates[:3])
            response = model_result["response"]
            selected_model = model_result["model"]
            status = "ok"
            self.brain_state.increment_metric("successful_replies")
        except LLMServiceError as e:
            print("❌ LLM error:", e)
            response = str(e)
            status = "llm_error"
            selected_model = ""
            self.brain_state.increment_metric("llm_errors")

        # -----------------------------
        # 4. SAFETY GUARD (ANTI-HALLUCINATION)
        # -----------------------------
        question_lower = message.lower()

        unsafe_patterns = [
            "what's in my",
            "what is in my",
            "what do i have in",
            "what's inside my"
        ]

        if any(p in question_lower for p in unsafe_patterns):
            if context_block == "No relevant memory.":
                response = "I don't have that information."

        # -----------------------------
        # 5. CLEAN OUTPUT
        # -----------------------------
        if "<assistant>" in response.lower():
            response = response.split("<assistant>")[-1].strip()

        # -----------------------------
        # 6. STORE MEMORY
        # -----------------------------
        try:
            self.memory.store_interaction(message, response)
        except Exception as e:
            print("❌ Memory store error:", e)

        evaluation = self.evaluator.evaluate(
            user_message=message,
            assistant_response=response.strip(),
            status=status,
            plan=plan,
        )

        self._log_interaction(
            user_message=message,
            assistant_response=response.strip(),
            memory_context=context_block,
            status=status,
            plan=plan,
            evaluation=evaluation,
        )
        self._store_lessons(
            user_message=message,
            assistant_response=response.strip(),
            status=status,
            plan=plan,
            evaluation=evaluation,
        )
        self.brain_state.record_evaluation(evaluation)
        sqlite_memory.log_interaction(
            user_message=message,
            assistant_response=response.strip(),
            status=status,
            model=selected_model,
        )

        return response.strip()

    def _log_interaction(
        self,
        *,
        user_message: str,
        assistant_response: str,
        memory_context: str,
        status: str,
        plan: dict,
        evaluation: dict,
    ):
        try:
            self.interaction_log.store(
                user_message=user_message,
                assistant_response=assistant_response,
                memory_context=memory_context,
                status=status,
                plan=plan,
                evaluation=evaluation,
            )
        except Exception as e:
            print("❌ Interaction log error:", e)

    def _store_lessons(
        self,
        *,
        user_message: str,
        assistant_response: str,
        status: str,
        plan: dict,
        evaluation: dict,
    ):
        try:
            reflection = self.reflection_service.reflect(
                user_message=user_message,
                assistant_response=assistant_response,
                status=status,
                plan=plan,
                evaluation=evaluation,
            )
            for lesson in reflection.get("lessons", []):
                self.brain_state.add_lesson(lesson)
            self.brain_state.update_self_model(
                strengths=reflection.get("strengths", []),
                weaknesses=reflection.get("weaknesses", []),
            )
        except Exception as e:
            print("❌ Reflection error:", e)

    def _format_lessons(self, lessons):
        if not lessons:
            return "No relevant lessons."

        return "\n".join(
            f"- {lesson['lesson']} (priority={lesson.get('priority', 1)}, count={lesson.get('count', 1)})"
            for lesson in lessons
        )

    def _format_brain_snapshot(self):
        self_model = self.brain_state.get_self_model()
        metrics = self.brain_state.get_metrics()
        recent_evaluations = self.brain_state.get_recent_evaluations(limit=3)

        strengths = ", ".join(self_model.get("strengths", [])) or "None"
        weaknesses = ", ".join(self_model.get("weaknesses", [])) or "None"
        evaluation_summary = "; ".join(
            f"{item.get('intent', 'unknown')}={item.get('overall', 0)}"
            for item in recent_evaluations
        ) or "None"

        return (
            f"Strengths: {strengths}\n"
            f"Weaknesses: {weaknesses}\n"
            f"Metrics: total={metrics.get('total_interactions', 0)}, "
            f"success={metrics.get('successful_replies', 0)}, "
            f"memory_hits={metrics.get('memory_hits', 0)}, "
            f"llm_errors={metrics.get('llm_errors', 0)}\n"
            f"Recent evaluations: {evaluation_summary}"
        )
