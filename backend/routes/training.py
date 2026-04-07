from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict

from backend.runtime import sqlite_memory, task_queue, topic_training_service, training_execution_service

router = APIRouter()


class TopicTrainingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    topic: str


@router.get("/topics")
def training_topics():
    return {
        "summary": sqlite_memory.summary(),
        "topics": sqlite_memory.list_training_topics(),
        "knowledge": sqlite_memory.latest_topic_knowledge(limit=10),
        "runs": training_execution_service.list_runs(limit=10),
    }


@router.post("/topics")
def enqueue_training_topic(req: TopicTrainingRequest):
    training = topic_training_service.enqueue_topic(
        message=f"Train on: {req.topic}",
        task_queue=task_queue,
    )
    return {
        "status": "queued",
        **training,
    }


@router.post("/runs/{dataset_id}/execute")
def execute_training_run(dataset_id: str):
    return training_execution_service.execute(dataset_id=dataset_id)
