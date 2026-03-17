import requests


class LLMService:

    def __init__(self):

        self.url = "http://localhost:11434/api/generate"
        self.model = "phi3"

    def generate(self, prompt):

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(self.url, json=payload)

        data = response.json()

        return data.get("response", "")