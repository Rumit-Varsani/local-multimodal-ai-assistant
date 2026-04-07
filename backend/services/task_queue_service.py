import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path


class TaskQueueService:
    def __init__(
        self,
        queue_path: str = "storage/jobs/queue.json",
        history_path: str = "storage/jobs/history.jsonl",
    ):
        self.queue_path = Path(queue_path)
        self.history_path = Path(history_path)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def enqueue(self, job_type: str, payload: dict | None = None, *, source: str = "manual", priority: int = 1):
        job = {
            "id": str(uuid.uuid4()),
            "type": job_type,
            "payload": payload or {},
            "status": "pending",
            "source": source,
            "priority": priority,
            "attempts": 0,
            "result": {},
            "last_error": "",
            "created_at": self._now(),
            "updated_at": self._now(),
        }
        with self._lock:
            queue = self._load_queue()
            queue["jobs"].append(job)
            queue["jobs"] = self._sorted_jobs(queue["jobs"])
            self._save_queue(queue)
        return job

    def list_jobs(self, *, include_completed: bool = True):
        queue = self._load_queue()
        jobs = queue["jobs"]
        if include_completed:
            return jobs
        return [job for job in jobs if job["status"] not in {"completed", "failed"}]

    def claim_next(self):
        with self._lock:
            queue = self._load_queue()
            for job in self._sorted_jobs(queue["jobs"]):
                if job["status"] == "pending":
                    return self._mark_running(queue, job)
        return None

    def claim_by_id(self, job_id: str):
        with self._lock:
            queue = self._load_queue()
            for job in queue["jobs"]:
                if job["id"] == job_id and job["status"] == "pending":
                    return self._mark_running(queue, job)
        return None

    def complete(self, job_id: str, result: dict | None = None):
        self._finalize(job_id, status="completed", result=result or {}, last_error="")

    def fail(self, job_id: str, error: str):
        self._finalize(job_id, status="failed", result={}, last_error=error)

    def stats(self):
        jobs = self._load_queue()["jobs"]
        return {
            "total": len(jobs),
            "pending": sum(1 for job in jobs if job["status"] == "pending"),
            "running": sum(1 for job in jobs if job["status"] == "running"),
            "completed": sum(1 for job in jobs if job["status"] == "completed"),
            "failed": sum(1 for job in jobs if job["status"] == "failed"),
        }

    def has_pending_job_type(self, job_type: str):
        jobs = self._load_queue()["jobs"]
        return any(job["type"] == job_type and job["status"] in {"pending", "running"} for job in jobs)

    def _finalize(self, job_id: str, *, status: str, result: dict, last_error: str):
        with self._lock:
            queue = self._load_queue()
            for job in queue["jobs"]:
                if job["id"] != job_id:
                    continue
                job["status"] = status
                job["result"] = result
                job["last_error"] = last_error
                job["updated_at"] = self._now()
                self._append_history(job)
                self._save_queue(queue)
                return

    def _append_history(self, job: dict):
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(job, ensure_ascii=True) + "\n")

    def _mark_running(self, queue: dict, job: dict):
        job["status"] = "running"
        job["attempts"] += 1
        job["updated_at"] = self._now()
        self._save_queue(queue)
        return job

    def _load_queue(self):
        if not self.queue_path.exists():
            return {"jobs": []}

        try:
            with self.queue_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return {"jobs": []}

    def _save_queue(self, queue: dict):
        with self.queue_path.open("w", encoding="utf-8") as handle:
            json.dump(queue, handle, ensure_ascii=True, indent=2)

    def _sorted_jobs(self, jobs: list[dict]):
        return sorted(jobs, key=lambda job: (-job.get("priority", 1), job.get("created_at", "")))

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
