import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class TrainingExecutionService:
    def __init__(self, runs_dir: str = "storage/checkpoints/runs"):
        self.runs_dir = Path(runs_dir)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.allow_execution = os.getenv("FORGEMIND_ENABLE_TRAINING_EXECUTION", "false").lower() == "true"

    def record_run(self, *, training_run: dict):
        run_id = training_run.get("dataset_id", "run")
        path = self.runs_dir / f"{run_id}.json"
        payload = {**training_run}
        payload.setdefault("updated_at", self._now())
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)
        payload["run_path"] = str(path)
        return payload

    def list_runs(self, limit: int = 20):
        runs = []
        for path in sorted(self.runs_dir.glob("*.json"), reverse=True):
            try:
                with path.open("r", encoding="utf-8") as handle:
                    item = json.load(handle)
            except Exception:
                continue
            item["run_path"] = str(path)
            runs.append(item)
            if len(runs) >= limit:
                break
        return runs

    def execute(self, *, dataset_id: str):
        path = self.runs_dir / f"{dataset_id}.json"
        if not path.exists():
            return {"status": "missing", "dataset_id": dataset_id}

        with path.open("r", encoding="utf-8") as handle:
            run = json.load(handle)

        if run.get("status") == "waiting":
            return {"status": "waiting", "dataset_id": dataset_id, "notes": run.get("notes", [])}

        if not self.allow_execution:
            run["status"] = "execution_disabled"
            run["updated_at"] = self._now()
            run["notes"] = run.get("notes", []) + ["Execution is disabled by FORGEMIND_ENABLE_TRAINING_EXECUTION=false."]
            return self.record_run(training_run=run)

        command = run.get("command", "")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        run["status"] = "completed" if result.returncode == 0 else "failed"
        run["updated_at"] = self._now()
        run["returncode"] = result.returncode
        run["stdout"] = result.stdout[-4000:]
        run["stderr"] = result.stderr[-4000:]
        return self.record_run(training_run=run)

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
