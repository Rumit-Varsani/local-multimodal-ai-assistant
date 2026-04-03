import json
from datetime import datetime, timezone
from pathlib import Path


class InteractionLogService:
    def __init__(self, log_path: str = "storage/interactions.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def store(
        self,
        *,
        user_message: str,
        assistant_response: str,
        memory_context: str,
        status: str,
        plan: dict | None = None,
        evaluation: dict | None = None,
    ) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "user_message": user_message,
            "assistant_response": assistant_response,
            "memory_context": memory_context,
            "plan": plan or {},
            "evaluation": evaluation or {},
        }

        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
