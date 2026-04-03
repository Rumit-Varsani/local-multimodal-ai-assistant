# backend/services/llm_service.py

import requests


class LLMService:
    def __init__(self):
        self.url = "http://127.0.0.1:11434/api/generate"
        self.model = "phi3"

    def generate(self, prompt: str):
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )

            result = response.json()
            return result.get("response", "No response")

        except Exception as e:
            print("❌ Ollama error:", e)
            return "Error connecting to model"