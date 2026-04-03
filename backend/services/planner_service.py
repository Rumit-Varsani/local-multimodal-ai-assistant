class PlannerService:
    def plan(self, *, message: str, preferences: dict, memory_hit: bool):
        message_lower = message.lower().strip()
        response_modes = preferences.get("response_modes", [])
        response_style = preferences.get("response_style", "")

        intent = "general_chat"
        strategy = "generate_with_context"

        if self._looks_like_preference_update(message_lower):
            intent = "preference_update"
            strategy = "direct_preference_ack"
        elif self._looks_like_personal_fact_question(message_lower):
            intent = "personal_memory_query"
            strategy = "direct_memory_lookup"
        elif self._looks_like_code_request(message_lower):
            intent = "code_generation"
            strategy = "generate_code_first"
        elif self._looks_like_explanation(message_lower):
            intent = "explanation"
            strategy = "generate_explanation"
        elif self._looks_like_unknown_personal_inventory(message_lower):
            intent = "unsupported_personal_inventory"
            strategy = "refuse_unknown_memory_guess"
        elif memory_hit:
            intent = "memory_grounded_chat"
            strategy = "generate_with_memory"

        return {
            "intent": intent,
            "strategy": strategy,
            "response_style": response_style or "default",
            "response_modes": response_modes,
        }

    def _looks_like_preference_update(self, message: str):
        return "i prefer" in message

    def _looks_like_personal_fact_question(self, message: str):
        patterns = [
            "what is my name",
            "what's my name",
            "where do i live",
            "what do i prefer",
            "what is my job",
            "what do i work as",
        ]
        return any(pattern in message for pattern in patterns)

    def _looks_like_code_request(self, message: str):
        patterns = ["write", "code", "python", "javascript", "function", "class", "script"]
        return any(pattern in message for pattern in patterns)

    def _looks_like_explanation(self, message: str):
        patterns = ["explain", "what is", "how does", "why does"]
        return any(pattern in message for pattern in patterns)

    def _looks_like_unknown_personal_inventory(self, message: str):
        patterns = ["what is in my", "what's in my", "what do i have in", "what's inside my"]
        return any(pattern in message for pattern in patterns)
