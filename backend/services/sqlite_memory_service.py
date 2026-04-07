import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class SQLiteMemoryService:
    def __init__(self, db_path: str = "storage/sqlite/forgemind.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def log_interaction(self, *, user_message: str, assistant_response: str, status: str, model: str = ""):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversation_events (timestamp, user_message, assistant_response, status, model)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self._now(), user_message, assistant_response, status, model),
            )

    def record_model_decision(self, *, task_type: str, selected_model: str, candidates: list[str], status: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO model_decisions (timestamp, task_type, selected_model, candidates_json, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self._now(), task_type, selected_model, json.dumps(candidates), status),
            )

    def create_training_topic(self, *, topic: str, subtopics: list[str]):
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO training_topics (created_at, updated_at, topic, status, subtopics_json, completed_subtopics_json, knowledge_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self._now(), self._now(), topic, "queued", json.dumps(subtopics), json.dumps([]), 0),
            )
            return cursor.lastrowid

    def update_training_topic(self, *, topic_id: int, status: str, completed_subtopics: list[str] | None = None):
        with self._connect() as conn:
            current = self.get_training_topic(topic_id)
            if current is None:
                return
            completed = completed_subtopics if completed_subtopics is not None else current["completed_subtopics"]
            conn.execute(
                """
                UPDATE training_topics
                SET updated_at = ?, status = ?, completed_subtopics_json = ?
                WHERE id = ?
                """,
                (self._now(), status, json.dumps(completed), topic_id),
            )

    def store_topic_knowledge(self, *, topic_id: int, topic: str, subtopic: str, model: str, answer: str, score: float):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO topic_knowledge (created_at, topic_id, topic, subtopic, model, answer, score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (self._now(), topic_id, topic, subtopic, model, answer, score),
            )
            conn.execute(
                """
                UPDATE training_topics
                SET updated_at = ?, knowledge_count = knowledge_count + 1
                WHERE id = ?
                """,
                (self._now(), topic_id),
            )

    def get_training_topic(self, topic_id: int):
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, created_at, updated_at, topic, status, subtopics_json, completed_subtopics_json, knowledge_count
                FROM training_topics
                WHERE id = ?
                """,
                (topic_id,),
            ).fetchone()
        return self._topic_from_row(row)

    def list_training_topics(self, limit: int = 20):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, created_at, updated_at, topic, status, subtopics_json, completed_subtopics_json, knowledge_count
                FROM training_topics
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._topic_from_row(row) for row in rows if row is not None]

    def summary(self):
        with self._connect() as conn:
            topics = conn.execute("SELECT COUNT(*) FROM training_topics").fetchone()[0]
            knowledge = conn.execute("SELECT COUNT(*) FROM topic_knowledge").fetchone()[0]
            decisions = conn.execute("SELECT COUNT(*) FROM model_decisions").fetchone()[0]
        return {
            "topics": topics,
            "knowledge_items": knowledge,
            "model_decisions": decisions,
        }

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _initialize(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    status TEXT NOT NULL,
                    model TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS model_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    selected_model TEXT NOT NULL,
                    candidates_json TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS training_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    status TEXT NOT NULL,
                    subtopics_json TEXT NOT NULL,
                    completed_subtopics_json TEXT NOT NULL,
                    knowledge_count INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS topic_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    topic_id INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    subtopic TEXT NOT NULL,
                    model TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    score REAL NOT NULL
                )
                """
            )

    def _topic_from_row(self, row):
        if row is None:
            return None
        return {
            "id": row[0],
            "created_at": row[1],
            "updated_at": row[2],
            "topic": row[3],
            "status": row[4],
            "subtopics": json.loads(row[5]),
            "completed_subtopics": json.loads(row[6]),
            "knowledge_count": row[7],
        }

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
