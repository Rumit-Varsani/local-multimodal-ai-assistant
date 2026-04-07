# backend/services/llm_service.py

import os

import requests
from dotenv import load_dotenv

load_dotenv()


class LLMServiceError(Exception):
    pass


class LLMService:
    def __init__(self):
        self.url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
        self.model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        self.timeout_seconds = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180"))
        self.tags_url = os.getenv("OLLAMA_TAGS_URL", "http://127.0.0.1:11434/api/tags")

    def generate(self, prompt: str, *, model: str | None = None):
        selected_model = model or self.model
        try:
            response = requests.post(
                self.url,
                json={
                    "model": selected_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            result = response.json()
        except requests.HTTPError as exc:
            details = self._build_http_error_message(exc.response)
            raise LLMServiceError(details) from exc
        except requests.Timeout as exc:
            raise LLMServiceError("Timed out while waiting for Ollama.") from exc
        except requests.RequestException as exc:
            raise LLMServiceError(f"Could not reach Ollama: {exc}") from exc
        except ValueError as exc:
            raise LLMServiceError("Ollama returned invalid JSON.") from exc

        content = result.get("response")
        if not isinstance(content, str) or not content.strip():
            raise LLMServiceError("Ollama returned an empty response.")

        return content

    def list_models(self):
        return self._fetch_available_models()

    def _build_http_error_message(self, response):
        if response is None:
            return "Ollama returned an unknown HTTP error."

        status_code = response.status_code
        if status_code == 404:
            available_models = self._fetch_available_models()
            model_hint = (
                f" Available models: {', '.join(available_models)}."
                if available_models else
                " Could not read available models from Ollama."
            )
            return (
                f"Ollama returned 404 for {self.url}. "
                f"Check that the Ollama API endpoint is correct and that model '{self.model}' exists."
                f"{model_hint}"
            )

        try:
            payload = response.json()
            error_text = payload.get("error") or str(payload)
        except ValueError:
            error_text = response.text.strip() or "No response body"

        return f"Ollama HTTP {status_code}: {error_text}"

    def _fetch_available_models(self):
        try:
            response = requests.get(self.tags_url, timeout=10)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return []

        models = payload.get("models", [])
        names = []
        for model in models:
            name = model.get("name")
            if name:
                names.append(name)

        return names
