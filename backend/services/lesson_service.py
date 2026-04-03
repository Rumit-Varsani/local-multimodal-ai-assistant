import json
from pathlib import Path


class LessonService:
    def __init__(self, lesson_path: str = "storage/lessons.jsonl"):
        self.lesson_path = Path(lesson_path)
        self.lesson_path.parent.mkdir(parents=True, exist_ok=True)

    def store_many(self, lessons):
        existing = self._load_all()
        seen_texts = {lesson["lesson"] for lesson in existing}

        with self.lesson_path.open("a", encoding="utf-8") as handle:
            for lesson in lessons:
                lesson_text = lesson.get("lesson", "").strip()
                if not lesson_text or lesson_text in seen_texts:
                    continue

                handle.write(json.dumps(lesson, ensure_ascii=True) + "\n")
                seen_texts.add(lesson_text)

    def find_relevant(self, query: str, limit: int = 5):
        query_tokens = self._tokenize(query)
        relevant = []

        for lesson in reversed(self._load_all()):
            lesson_tokens = set(lesson.get("tags", [])) | self._tokenize(lesson.get("lesson", ""))
            score = len(query_tokens.intersection(lesson_tokens))

            if score > 0:
                relevant.append((score, lesson))

        relevant.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in relevant[:limit]]

    def _load_all(self):
        if not self.lesson_path.exists():
            return []

        lessons = []
        with self.lesson_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    lessons.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return lessons

    def _tokenize(self, text: str):
        tokens = set()
        for raw_token in text.lower().split():
            token = raw_token.strip(".,!?;:'\"()[]{}")
            if len(token) >= 3:
                tokens.add(token)
        return tokens
