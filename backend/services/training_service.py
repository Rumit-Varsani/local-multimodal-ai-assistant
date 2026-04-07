import json
from datetime import datetime, timezone
from pathlib import Path


class TrainingService:
    def __init__(self, plans_dir: str = "storage/checkpoints/plans"):
        self.plans_dir = Path(plans_dir)
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    def plan_training(self, *, dataset: dict, student_model: dict):
        sample_count = dataset.get("filtered_samples", 0)
        strategy = "hold"
        if sample_count >= 10:
            strategy = "qlora"
        if sample_count >= 75:
            strategy = "lora-extended"

        plan = {
            "created_at": self._now(),
            "student_model": student_model,
            "dataset_id": dataset.get("dataset_id", ""),
            "sample_count": sample_count,
            "strategy": strategy,
            "status": "planned",
            "notes": self._notes(strategy, sample_count),
        }
        plan_path = self.plans_dir / f"{dataset.get('dataset_id', 'dataset')}.json"
        with plan_path.open("w", encoding="utf-8") as handle:
            json.dump(plan, handle, ensure_ascii=True, indent=2)

        plan["plan_path"] = str(plan_path)
        return plan

    def _notes(self, strategy: str, sample_count: int):
        if strategy == "hold":
            return [f"Only {sample_count} filtered samples are available; wait for more training data."]
        if strategy == "qlora":
            return ["Ready for a small Phase 1 QLoRA training run on the current student model."]
        return ["Ready for a larger LoRA-style autonomous training cycle."]

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
