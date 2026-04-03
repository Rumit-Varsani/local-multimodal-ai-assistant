# backend/services/llm_service.py

import requests


class LLMServiceError(Exception):
    pass


class LLMService:
    def __init__(self):
        self.url = "http://127.0.0.1:11434/api/generate"
        self.model = "phi3"
        self.timeout_seconds = 60

    def generate(self, prompt: str):
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            result = response.json()
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
