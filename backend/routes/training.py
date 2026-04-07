from fastapi import APIRouter

from backend.runtime import sqlite_memory

router = APIRouter()


@router.get("/topics")
def training_topics():
    return {
        "summary": sqlite_memory.summary(),
        "topics": sqlite_memory.list_training_topics(),
    }
