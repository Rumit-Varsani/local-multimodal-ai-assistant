from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from backend.runtime import autonomy_agent, checkpoint_registry, task_queue

router = APIRouter()


class EnqueueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    priority: int = 2


@router.get("/status")
def autonomy_status():
    return autonomy_agent.status()


@router.post("/start")
def start_autonomy():
    return autonomy_agent.start()


@router.post("/stop")
def stop_autonomy():
    return autonomy_agent.stop()


@router.post("/run-once")
def run_once():
    return autonomy_agent.run_once()


@router.post("/jobs/autonomy-cycle")
def enqueue_autonomy_cycle(req: EnqueueRequest):
    return task_queue.enqueue("autonomy_cycle", source="api", priority=req.priority)


@router.get("/jobs")
def list_jobs():
    return {
        "stats": task_queue.stats(),
        "jobs": task_queue.list_jobs(),
    }


@router.get("/checkpoints")
def list_checkpoints():
    return {
        "promoted": checkpoint_registry.get_promoted(),
        "items": checkpoint_registry.list_checkpoints(),
    }
