import os
import threading
import time
from datetime import datetime, timezone


class AutonomyAgent:
    def __init__(
        self,
        *,
        task_queue,
        dataset_builder,
        model_registry,
        training_service,
        benchmark_service,
        checkpoint_registry,
        interaction_log,
    ):
        self.task_queue = task_queue
        self.dataset_builder = dataset_builder
        self.model_registry = model_registry
        self.training_service = training_service
        self.benchmark_service = benchmark_service
        self.checkpoint_registry = checkpoint_registry
        self.interaction_log = interaction_log
        self.poll_seconds = 30
        self.auto_start = False
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._state = {
            "running": False,
            "last_cycle_at": "",
            "last_result": {},
            "last_error": "",
        }
        self.refresh_config_from_env()

    def refresh_config_from_env(self):
        self.poll_seconds = int(os.getenv("AUTONOMY_POLL_SECONDS", "30"))
        self.auto_start = os.getenv("AUTONOMY_AUTO_START", "false").lower() == "true"

    def start(self):
        self.refresh_config_from_env()
        with self._lock:
            if self._thread and self._thread.is_alive():
                return self.status()

            self._stop_event.clear()
            self._thread = threading.Thread(target=self._loop, daemon=True, name="forgemind-autonomy")
            self._thread.start()
            self._state["running"] = True
            return self.status()

    def stop(self):
        self._stop_event.set()
        thread = self._thread
        if thread and thread.is_alive():
            thread.join(timeout=min(self.poll_seconds, 5))
        with self._lock:
            self._state["running"] = False
        return self.status()

    def status(self):
        running = bool(self._thread and self._thread.is_alive())
        self._state["running"] = running
        return {
            **self._state,
            "auto_start": self.auto_start,
            "poll_seconds": self.poll_seconds,
            "queue": self.task_queue.stats(),
            "checkpoints": len(self.checkpoint_registry.list_checkpoints()),
            "student": self.model_registry.get_student(),
        }

    def enqueue_cycle(self, *, source: str = "manual", priority: int = 2):
        return self.task_queue.enqueue("autonomy_cycle", source=source, priority=priority)

    def run_once(self):
        queued_job = self.task_queue.enqueue("autonomy_cycle", source="manual_run_once", priority=3)
        job = self.task_queue.claim_by_id(queued_job["id"])
        if job is None:
            return {"error": "Could not claim the queued autonomy cycle."}
        return self._process_job(job)

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                self._ensure_work_available()
                job = self.task_queue.claim_next()
                if job is not None:
                    self._process_job(job)
            except Exception as exc:
                self._state["last_error"] = str(exc)
            time.sleep(self.poll_seconds)

    def _ensure_work_available(self):
        if not self.task_queue.has_pending_job_type("autonomy_cycle"):
            self.task_queue.enqueue("autonomy_cycle", source="autonomous_idle_cycle", priority=1)

    def _process_job(self, job: dict):
        try:
            if job["type"] != "autonomy_cycle":
                result = {"message": f"Unsupported job type: {job['type']}"}
            else:
                result = self._run_cycle()
            self.task_queue.complete(job["id"], result=result)
            self._state["last_result"] = result
            self._state["last_error"] = ""
            self._state["last_cycle_at"] = self._now()
            return result
        except Exception as exc:
            error = str(exc)
            self.task_queue.fail(job["id"], error)
            self._state["last_error"] = error
            self._state["last_cycle_at"] = self._now()
            return {"error": error}

    def _run_cycle(self):
        dataset = self.dataset_builder.build_dataset()
        dataset_benchmark = self.benchmark_service.evaluate_dataset(dataset)
        student = self.model_registry.get_student()
        training_plan = self.training_service.plan_training(dataset=dataset, student_model=student)

        if not dataset_benchmark["ready_for_training"]:
            return {
                "status": "waiting_for_more_data",
                "dataset": dataset,
                "dataset_benchmark": dataset_benchmark,
                "training_plan": training_plan,
            }

        checkpoint = self.checkpoint_registry.register_candidate(
            dataset=dataset,
            training_plan=training_plan,
            benchmark=dataset_benchmark,
        )
        promoted = self._maybe_promote(checkpoint)
        return {
            "status": "checkpoint_created",
            "dataset": dataset,
            "dataset_benchmark": dataset_benchmark,
            "training_plan": training_plan,
            "checkpoint": checkpoint,
            "promoted_checkpoint": promoted,
        }

    def _maybe_promote(self, checkpoint: dict):
        current = self.checkpoint_registry.get_promoted()
        checkpoint_eval = self.benchmark_service.evaluate_checkpoint(
            checkpoint=checkpoint,
            current_promoted=current,
        )
        if checkpoint_eval["should_promote"]:
            promoted = self.checkpoint_registry.promote(checkpoint["id"])
            promoted["promotion_evaluation"] = checkpoint_eval
            return promoted
        checkpoint["promotion_evaluation"] = checkpoint_eval
        return None

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
