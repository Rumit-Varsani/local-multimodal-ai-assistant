from backend.services.llm_service import LLMService, LLMServiceError


class MultiModelOllamaService:
    def __init__(self):
        self.llm = LLMService()

    def list_models(self):
        return self.llm.list_models()

    def generate(self, *, prompt: str, models: list[str]):
        errors = []
        for model in models:
            try:
                response = self.llm.generate(prompt, model=model)
                return {
                    "model": model,
                    "response": response,
                    "errors": errors,
                }
            except LLMServiceError as exc:
                errors.append({"model": model, "error": str(exc)})

        raise LLMServiceError(
            "All candidate models failed. "
            + "; ".join(f"{item['model']}: {item['error']}" for item in errors)
        )

    def compare(self, *, prompt: str, models: list[str]):
        results = []
        for model in models:
            try:
                response = self.llm.generate(prompt, model=model)
                results.append({"model": model, "response": response, "error": ""})
            except LLMServiceError as exc:
                results.append({"model": model, "response": "", "error": str(exc)})
        return results
