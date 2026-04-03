class EvaluationService:
    def evaluate(self, *, user_message: str, assistant_response: str, status: str, plan: dict):
        response = assistant_response.strip()
        message_lower = user_message.lower()
        response_lower = response.lower()

        correctness = 0.6
        usefulness = 0.6
        brevity = 0.6
        safety = 0.9
        preference_alignment = 0.6
        notes = []

        if status in {"llm_error"}:
            correctness = 0.2
            usefulness = 0.2
            notes.append("The local model failed to answer.")

        if "i don't have that information" in response_lower:
            correctness = max(correctness, 0.8)
            safety = max(safety, 0.95)
            notes.append("Avoided guessing without memory or evidence.")

        if plan.get("intent") == "code_generation":
            if "```" in response or "def " in response or "print(" in response or "class " in response:
                usefulness = 0.9
                notes.append("Returned executable-looking code.")
            else:
                usefulness = 0.4
                notes.append("Coding request did not clearly return code.")

        if plan.get("response_style") == "short":
            if len(response) <= 180:
                brevity = 0.95
                preference_alignment = 0.95
                notes.append("Response matched the user's short-answer preference.")
            else:
                brevity = 0.45
                preference_alignment = 0.45
                notes.append("Response was longer than the user's short-answer preference.")

        if plan.get("intent") == "personal_memory_query":
            if "your name is" in response_lower or "you prefer" in response_lower or "you live in" in response_lower:
                correctness = 0.95
                usefulness = 0.9
                notes.append("Personal fact was answered directly.")

        overall = round((correctness + usefulness + brevity + safety + preference_alignment) / 5, 2)

        return {
            "overall": overall,
            "correctness": round(correctness, 2),
            "usefulness": round(usefulness, 2),
            "brevity": round(brevity, 2),
            "safety": round(safety, 2),
            "preference_alignment": round(preference_alignment, 2),
            "notes": notes,
            "intent": plan.get("intent", ""),
            "strategy": plan.get("strategy", ""),
        }
