import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class CheckpointRegistryService:
    DEFAULT_REGISTRY = {
        "promoted_checkpoint_id": "",
        "checkpoints": [],
    }

    def __init__(self, registry_path: str = "storage/checkpoints/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

    def list_checkpoints(self):
        return self._load()["checkpoints"]

    def register_candidate(self, *, dataset: dict, training_plan: dict, benchmark: dict):
        registry = self._load()
        checkpoint_id = f"ckpt-{uuid.uuid4().hex[:12]}"
        checkpoint = {
            "id": checkpoint_id,
            "status": "candidate",
            "dataset": dataset,
            "training_plan": training_plan,
            "benchmark": benchmark,
            "promoted": False,
            "created_at": self._now(),
        }
        registry["checkpoints"].append(checkpoint)
        self._save(registry)
        return checkpoint

    def promote(self, checkpoint_id: str):
        registry = self._load()
        promoted = None
        for checkpoint in registry["checkpoints"]:
            checkpoint["promoted"] = checkpoint["id"] == checkpoint_id
            if checkpoint["promoted"]:
                checkpoint["status"] = "promoted"
                promoted = checkpoint
            elif checkpoint["status"] == "promoted":
                checkpoint["status"] = "archived"

        if promoted is not None:
            registry["promoted_checkpoint_id"] = checkpoint_id
            self._save(registry)
        return promoted

    def get_promoted(self):
        registry = self._load()
        promoted_id = registry.get("promoted_checkpoint_id", "")
        for checkpoint in registry["checkpoints"]:
            if checkpoint["id"] == promoted_id:
                return checkpoint
        return None

    def _load(self):
        if not self.registry_path.exists():
            return dict(self.DEFAULT_REGISTRY)
        try:
            with self.registry_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return dict(self.DEFAULT_REGISTRY)

    def _save(self, registry: dict):
        with self.registry_path.open("w", encoding="utf-8") as handle:
            json.dump(registry, handle, ensure_ascii=True, indent=2)

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
