import json
from pathlib import Path


class ModelRegistryService:
    DEFAULT_REGISTRY = {
        "student": {
            "name": "ForgeMind",
            "model_id": "forgemind-core",
            "base_model": "qwen3-8b",
            "stage": "phase1",
            "role": "student",
        },
        "teachers": [
            {
                "name": "Qwen Teacher",
                "model_id": "qwen3-32b",
                "role": "reasoning_teacher",
            },
            {
                "name": "Llama Teacher",
                "model_id": "llama-3.3-70b-instruct",
                "role": "assistant_teacher",
            },
            {
                "name": "Devstral Teacher",
                "model_id": "devstral",
                "role": "code_teacher",
            },
        ],
        "embeddings": {
            "name": "all-MiniLM-L6-v2",
            "role": "retrieval_embedding",
        },
    }

    def __init__(self, registry_path: str = "storage/models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        if not self.registry_path.exists():
            self.save(self.DEFAULT_REGISTRY)
            return dict(self.DEFAULT_REGISTRY)

        try:
            with self.registry_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            self.save(self.DEFAULT_REGISTRY)
            return dict(self.DEFAULT_REGISTRY)

        registry = dict(self.DEFAULT_REGISTRY)
        registry.update(data)
        return registry

    def save(self, registry: dict):
        with self.registry_path.open("w", encoding="utf-8") as handle:
            json.dump(registry, handle, ensure_ascii=True, indent=2)

    def get_student(self):
        return self.load()["student"]

    def get_teachers(self):
        return self.load()["teachers"]
