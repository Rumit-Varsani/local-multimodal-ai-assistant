class RouterService:
    def classify(self, message: str):
        normalized = message.lower().strip()
        if normalized.startswith("train yourself on:") or normalized.startswith("train on:"):
            return {"kind": "topic_training", "task_type": "training"}
        if any(word in normalized for word in ["code", "python", "function", "class", "script"]):
            return {"kind": "chat", "task_type": "code_generation"}
        return {"kind": "chat", "task_type": "general_chat"}
