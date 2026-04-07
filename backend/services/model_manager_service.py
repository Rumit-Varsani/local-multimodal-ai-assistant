import os


class ModelManagerService:
    DEFAULT_TASK_PROFILES = {
        "general_chat": ["mistral", "llama3", "phi3:mini"],
        "code_generation": ["llama3", "mistral", "phi3:mini"],
        "training": ["llama3", "mistral", "phi3:mini"],
        "evaluation": ["llama3", "mistral", "phi3:mini"],
    }

    def __init__(self, multi_model_service):
        self.multi_model_service = multi_model_service
        preferred = os.getenv("FORGEMIND_MODEL_CANDIDATES", "mistral,llama3,phi3:mini")
        self.preferred_models = [item.strip() for item in preferred.split(",") if item.strip()]
        self.allow_heavy_models = os.getenv("FORGEMIND_ALLOW_HEAVY_MODELS", "false").lower() == "true"

    def available_models(self):
        available = self.multi_model_service.list_models()
        if not available:
            return list(self.preferred_models)
        return available

    def choose_candidates(self, task_type: str):
        available = self.available_models()
        preferred = self.DEFAULT_TASK_PROFILES.get(task_type, self.preferred_models)
        ordered = []

        for model in preferred + self.preferred_models + available:
            if model not in available:
                continue
            if not self.allow_heavy_models and self._looks_heavy(model):
                continue
            if model not in ordered:
                ordered.append(model)

        if ordered:
            return ordered
        return available[:1] if available else list(self.preferred_models)

    def describe_routing(self, task_type: str):
        return {
            "task_type": task_type,
            "candidates": self.choose_candidates(task_type),
            "allow_heavy_models": self.allow_heavy_models,
        }

    def _looks_heavy(self, model: str):
        lowered = model.lower()
        return any(tag in lowered for tag in ["70b", "34b", "32b", "27b", "24b", "22b", "14b"])
