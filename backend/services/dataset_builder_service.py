import json
from datetime import datetime, timezone
from pathlib import Path


class DatasetBuilderService:
    def __init__(
        self,
        *,
        teacher_service=None,
        critic_service=None,
        interactions_path: str = "storage/interactions.jsonl",
        raw_dir: str = "storage/datasets/raw",
        filtered_dir: str = "storage/datasets/filtered",
    ):
        self.teacher_service = teacher_service
        self.critic_service = critic_service
        self.interactions_path = Path(interactions_path)
        self.raw_dir = Path(raw_dir)
        self.filtered_dir = Path(filtered_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.filtered_dir.mkdir(parents=True, exist_ok=True)

    def build_dataset(self, *, max_records: int = 200):
        interactions = self._load_interactions()
        raw_samples = []
        filtered_samples = []
        seen_pairs = set()

        for record in interactions[-max_records:]:
            sample = self._to_sample(record)
            if not sample:
                continue

            raw_samples.append(sample)
            self._add_filtered_sample(sample, filtered_samples, seen_pairs)

        enriched_samples = self._build_teacher_samples(filtered_samples)
        for sample in enriched_samples:
            raw_samples.append(sample)
            self._add_filtered_sample(sample, filtered_samples, seen_pairs)

        dataset_id = self._dataset_id()
        raw_path = self.raw_dir / f"{dataset_id}.jsonl"
        filtered_path = self.filtered_dir / f"{dataset_id}.jsonl"
        self._write_jsonl(raw_path, raw_samples)
        self._write_jsonl(filtered_path, filtered_samples)

        return {
            "dataset_id": dataset_id,
            "created_at": self._now(),
            "raw_path": str(raw_path),
            "filtered_path": str(filtered_path),
            "raw_samples": len(raw_samples),
            "filtered_samples": len(filtered_samples),
            "teacher_samples": len(enriched_samples),
        }

    def _load_interactions(self):
        if not self.interactions_path.exists():
            return []

        records = []
        with self.interactions_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return records

    def _to_sample(self, record: dict):
        user_message = str(record.get("user_message", "")).strip()
        assistant_response = str(record.get("assistant_response", "")).strip()
        status = str(record.get("status", "")).strip()

        if not user_message or not assistant_response:
            return None
        if status == "llm_error":
            return None
        if assistant_response == "Please provide a message.":
            return None

        return {
            "input": user_message,
            "output": assistant_response,
            "status": status,
            "plan": record.get("plan", {}),
            "evaluation": record.get("evaluation", {}),
            "memory_context": record.get("memory_context", ""),
        }

    def _write_jsonl(self, path: Path, items: list[dict]):
        with path.open("w", encoding="utf-8") as handle:
            for item in items:
                handle.write(json.dumps(item, ensure_ascii=True) + "\n")

    def _build_teacher_samples(self, filtered_samples: list[dict]):
        if not self.teacher_service:
            return []
        return self.teacher_service.enrich_samples(filtered_samples)

    def _add_filtered_sample(self, sample: dict, filtered_samples: list[dict], seen_pairs: set):
        key = (sample["input"], sample["output"])
        if key in seen_pairs:
            return

        if self.critic_service:
            critique = self.critic_service.score_sample(sample)
            sample["critic"] = critique
            if not critique["accepted"]:
                return

        seen_pairs.add(key)
        filtered_samples.append(sample)

    def _dataset_id(self):
        return datetime.now(timezone.utc).strftime("dataset-%Y%m%dT%H%M%SZ")

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
