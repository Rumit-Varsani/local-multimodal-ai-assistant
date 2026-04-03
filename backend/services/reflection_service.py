class ReflectionService:
    def reflect(self, *, user_message: str, assistant_response: str, status: str, plan: dict, evaluation: dict):
        message = user_message.lower()
        response = assistant_response.lower()
        lessons = []
        strengths = []
        weaknesses = []

        if any(phrase in message for phrase in ["my name is", "i live", "i work", "i like", "i prefer"]):
            lessons.append({
                "lesson": "When the user shares a personal fact, store it and use direct recall for later personal questions.",
                "tags": ["memory", "personal", "recall"],
                "source": "reflection",
                "priority": 4,
            })

        if "what is my name" in message or "what's my name" in message:
            lessons.append({
                "lesson": "For personal fact questions, answer directly from stored memory instead of letting the model guess.",
                "tags": ["memory", "name", "recall"],
                "source": "reflection",
                "priority": 5,
            })

        if any(phrase in message for phrase in ["write", "code", "python", "javascript", "function", "class"]):
            lessons.append({
                "lesson": "For coding requests, prefer returning working code first and keep extra explanation brief.",
                "tags": ["code", "programming", "python", "javascript"],
                "source": "reflection",
                "priority": 4,
            })

        if "i don't have that information" in response:
            lessons.append({
                "lesson": "When memory or evidence is missing, say you do not have that information instead of guessing.",
                "tags": ["memory", "uncertainty", "accuracy"],
                "source": "reflection",
                "priority": 5,
            })

        if status == "llm_error":
            lessons.append({
                "lesson": "If the local model is unavailable, clearly explain the connection or timeout problem.",
                "tags": ["reliability", "ollama", "errors"],
                "source": "reflection",
                "priority": 5,
            })
            weaknesses.append("Depends on local model availability.")

        if len(assistant_response) > 220 or evaluation.get("preference_alignment", 1.0) < 0.6:
            lessons.append({
                "lesson": "When the user prefers short answers, keep the response compact and avoid unnecessary elaboration.",
                "tags": ["style", "concise"],
                "source": "reflection",
                "priority": 4,
            })
            weaknesses.append("Sometimes answers are more verbose than the user's preference.")

        if evaluation.get("overall", 0) >= 0.85:
            strengths.append(f"Handles {plan.get('intent', 'general')} requests reliably.")

        if plan.get("strategy") == "direct_memory_lookup":
            strengths.append("Can answer structured personal-memory questions directly.")

        return {
            "lessons": lessons,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }
