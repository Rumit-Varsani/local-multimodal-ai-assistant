import json
import os
from datetime import datetime, timezone
from pathlib import Path


class TrainingService:
    def __init__(
        self,
        plans_dir: str = "storage/checkpoints/plans",
        runs_dir: str = "storage/checkpoints/runs",
    ):
        self.plans_dir = Path(plans_dir)
        self.runs_dir = Path(runs_dir)
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)

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

    def create_training_run(self, *, dataset: dict, training_plan: dict):
        command_template = os.getenv(
            "FORGEMIND_TRAIN_COMMAND",
            "python train_forgemind.py --dataset {dataset_path} --strategy {strategy}",
        )
        dataset_path = dataset.get("filtered_path", "")
        strategy = training_plan.get("strategy", "hold")
        command = command_template.format(
            dataset_path=dataset_path,
            strategy=strategy,
        )

        run = {
            "created_at": self._now(),
            "dataset_id": dataset.get("dataset_id", ""),
            "strategy": strategy,
            "status": "ready" if strategy != "hold" else "waiting",
            "command": command,
            "notes": training_plan.get("notes", []),
        }
        run_path = self.runs_dir / f"{dataset.get('dataset_id', 'dataset')}.json"
        with run_path.open("w", encoding="utf-8") as handle:
            json.dump(run, handle, ensure_ascii=True, indent=2)
        run["run_path"] = str(run_path)
        return run

    def _notes(self, strategy: str, sample_count: int):
        if strategy == "hold":
            return [f"Only {sample_count} filtered samples are available; wait for more training data."]
        if strategy == "qlora":
            return ["Ready for a small Phase 1 QLoRA training run on the current student model."]
        return ["Ready for a larger LoRA-style autonomous training cycle."]

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
