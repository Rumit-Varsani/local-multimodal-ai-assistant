import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


class BrainStateService:
    DEFAULT_STATE = {
        "preferences": {
            "response_style": "",
            "response_modes": [],
        },
        "facts": {
            "name": "",
            "location": "",
            "work": "",
            "likes": "",
            "preference": "",
        },
        "procedural_lessons": [],
        "self_model": {
            "strengths": [],
            "weaknesses": [],
            "last_updated": "",
        },
        "metrics": {
            "total_interactions": 0,
            "successful_replies": 0,
            "memory_hits": 0,
            "llm_errors": 0,
            "preference_updates": 0,
        },
        "recent_evaluations": [],
        "last_updated": "",
    }

    def __init__(self, state_path: str = "storage/brain_state.json"):
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self):
        if not self.state_path.exists():
            return deepcopy(self.DEFAULT_STATE)

        try:
            with self.state_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return deepcopy(self.DEFAULT_STATE)

        state = deepcopy(self.DEFAULT_STATE)
        self._deep_merge(state, data)
        return state

    def save(self, state):
        state["last_updated"] = self._now()
        with self.state_path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=True, indent=2)

    def update_fact(self, fact_key: str, value: str):
        if not value:
            return

        state = self.load()
        if fact_key in state["facts"]:
            state["facts"][fact_key] = value
        self.save(state)

    def update_preference(self, preference_value: str):
        if not preference_value:
            return

        state = self.load()
        state["facts"]["preference"] = preference_value
        state["preferences"]["response_style"] = self._normalize_response_style(preference_value)
        state["preferences"]["response_modes"] = self._extract_response_modes(preference_value)
        self.save(state)

    def get_fact(self, fact_key: str):
        state = self.load()
        return state["facts"].get(fact_key, "").strip()

    def get_preferences(self):
        state = self.load()
        return state["preferences"]

    def get_self_model(self):
        state = self.load()
        return state["self_model"]

    def get_metrics(self):
        state = self.load()
        return state["metrics"]

    def get_recent_evaluations(self, limit: int = 5):
        state = self.load()
        return state["recent_evaluations"][-limit:]

    def add_lesson(self, lesson):
        lesson_text = lesson.get("lesson", "").strip()
        if not lesson_text:
            return

        state = self.load()
        lessons = state["procedural_lessons"]

        for existing in lessons:
            if existing.get("lesson") == lesson_text:
                existing["priority"] = max(existing.get("priority", 1), lesson.get("priority", 1))
                existing["count"] = existing.get("count", 1) + 1
                existing["tags"] = sorted(set(existing.get("tags", [])) | set(lesson.get("tags", [])))
                existing["last_updated"] = self._now()
                self.save(state)
                return

        new_lesson = {
            "lesson": lesson_text,
            "tags": lesson.get("tags", []),
            "priority": lesson.get("priority", 1),
            "count": 1,
            "source": lesson.get("source", "reflection"),
            "last_updated": self._now(),
        }
        lessons.append(new_lesson)
        lessons.sort(key=lambda item: (item.get("priority", 1), item.get("count", 1)), reverse=True)
        state["procedural_lessons"] = lessons[-50:]
        self.save(state)

    def find_relevant_lessons(self, query: str, limit: int = 5):
        state = self.load()
        query_tokens = self._tokenize(query)
        matches = []

        for lesson in state["procedural_lessons"]:
            lesson_tokens = set(lesson.get("tags", [])) | self._tokenize(lesson.get("lesson", ""))
            score = len(query_tokens.intersection(lesson_tokens)) + lesson.get("priority", 1)
            if score > lesson.get("priority", 1):
                matches.append((score, lesson))

        matches.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in matches[:limit]]

    def update_self_model(self, strengths=None, weaknesses=None):
        state = self.load()
        if strengths:
            state["self_model"]["strengths"] = sorted(set(state["self_model"]["strengths"]) | set(strengths))[-10:]
        if weaknesses:
            state["self_model"]["weaknesses"] = sorted(set(state["self_model"]["weaknesses"]) | set(weaknesses))[-10:]
        state["self_model"]["last_updated"] = self._now()
        self.save(state)

    def record_evaluation(self, evaluation):
        state = self.load()
        state["recent_evaluations"].append({
            "timestamp": self._now(),
            **evaluation,
        })
        state["recent_evaluations"] = state["recent_evaluations"][-20:]
        self.save(state)

    def increment_metric(self, metric_key: str):
        state = self.load()
        if metric_key in state["metrics"]:
            state["metrics"][metric_key] += 1
        self.save(state)

    def _normalize_response_style(self, preference_value: str):
        lowered = preference_value.lower()
        if "short" in lowered or "brief" in lowered or "concise" in lowered:
            return "short"
        if "detailed" in lowered or "long" in lowered or "depth" in lowered:
            return "detailed"
        return preference_value.strip()

    def _extract_response_modes(self, preference_value: str):
        lowered = preference_value.lower()
        modes = []
        if "short" in lowered or "brief" in lowered or "concise" in lowered:
            modes.append("short")
        if "detailed" in lowered or "long" in lowered:
            modes.append("detailed")
        if "step" in lowered:
            modes.append("step-by-step")
        if "code" in lowered:
            modes.append("code-first")
        return modes

    def _tokenize(self, text: str):
        tokens = set()
        for raw_token in text.lower().split():
            token = raw_token.strip(".,!?;:'\"()[]{}")
            if len(token) >= 3:
                tokens.add(token)
        return tokens

    def _deep_merge(self, base, extra):
        for key, value in extra.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _now(self):
        return datetime.now(timezone.utc).isoformat()
