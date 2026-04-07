import json
import os

from backend.services.evaluation_service import EvaluationService
from backend.services.llm_service import LLMService, LLMServiceError


class JudgeService:
    def __init__(self):
        self.enabled = os.getenv("FORGEMIND_ENABLE_LLM_JUDGE", "false").lower() == "true"
        self.max_candidates = int(os.getenv("FORGEMIND_JUDGE_MAX_CANDIDATES", "3"))
        self.fallback_evaluator = EvaluationService()
        self.llm = LLMService()

    def rank_candidates(self, *, prompt: str, candidates: list[dict], task_type: str):
        trimmed = [item for item in candidates if item.get("response")] [: self.max_candidates]
        if not trimmed:
            return []

        heuristic_ranked = self._heuristic_rank(prompt=prompt, candidates=trimmed, task_type=task_type)
        if not self.enabled or len(heuristic_ranked) < 2:
            return heuristic_ranked

        llm_ranked = self._llm_rank(prompt=prompt, candidates=heuristic_ranked, task_type=task_type)
        return llm_ranked or heuristic_ranked

    def _heuristic_rank(self, *, prompt: str, candidates: list[dict], task_type: str):
        ranked = []
        for item in candidates:
            evaluation = self.fallback_evaluator.evaluate(
                user_message=prompt,
                assistant_response=item["response"],
                status="ok",
                plan={"intent": task_type, "strategy": "judge_heuristic", "response_style": "default"},
            )
            ranked.append(
                {
                    **item,
                    "judge_score": evaluation["overall"],
                    "judge_method": "heuristic",
                    "judge_notes": evaluation["notes"],
                    "evaluation": evaluation,
                }
            )

        ranked.sort(key=lambda candidate: candidate["judge_score"], reverse=True)
        return ranked

    def _llm_rank(self, *, prompt: str, candidates: list[dict], task_type: str):
        judge_prompt = self._build_judge_prompt(prompt=prompt, candidates=candidates, task_type=task_type)
        try:
            response = self.llm.generate(judge_prompt)
        except LLMServiceError:
            return []

        parsed = self._parse_judge_response(response)
        if not parsed:
            return []

        by_model = {item["model"]: item for item in candidates}
        ranked = []
        for item in parsed:
            model = item["model"]
            if model not in by_model:
                continue
            ranked.append(
                {
                    **by_model[model],
                    "judge_score": item["score"],
                    "judge_method": "llm_judge",
                    "judge_notes": item["notes"],
                }
            )

        if not ranked:
            return []

        ranked.sort(key=lambda candidate: candidate["judge_score"], reverse=True)
        return ranked

    def _build_judge_prompt(self, *, prompt: str, candidates: list[dict], task_type: str):
        rendered = []
        for item in candidates:
            rendered.append(f"Model: {item['model']}\nAnswer:\n{item['response']}")

        return f"""
You are ranking candidate model answers for ForgeMind.

Task type: {task_type}
User/task prompt:
{prompt}

Candidates:
{chr(10).join(rendered)}

Return JSON only, as a list like:
[
  {{"model":"name","score":0.82,"notes":["reason"]}}
]

Scoring rules:
- reward correctness, clarity, practical usefulness, and consistency
- penalize vagueness, hallucination, and missing substance
- scores must be between 0.0 and 1.0
"""

    def _parse_judge_response(self, response: str):
        try:
            payload = json.loads(response.strip())
        except json.JSONDecodeError:
            return []

        if not isinstance(payload, list):
            return []

        parsed = []
        for item in payload:
            model = str(item.get("model", "")).strip()
            if not model:
                continue
            try:
                score = float(item.get("score", 0.0))
            except (TypeError, ValueError):
                score = 0.0
            notes = item.get("notes", [])
            if not isinstance(notes, list):
                notes = []
            parsed.append(
                {
                    "model": model,
                    "score": round(max(0.0, min(score, 1.0)), 2),
                    "notes": [str(note) for note in notes[:3]],
                }
            )
        return parsed
