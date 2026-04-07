from fastapi import APIRouter

from backend.runtime import sqlite_memory, training_execution_service

router = APIRouter()


@router.get("/topics")
def training_topics():
    return {
        "summary": sqlite_memory.summary(),
        "topics": sqlite_memory.list_training_topics(),
        "knowledge": sqlite_memory.latest_topic_knowledge(limit=10),
        "runs": training_execution_service.list_runs(limit=10),
    }
