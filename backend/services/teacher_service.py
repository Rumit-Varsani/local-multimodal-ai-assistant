import json
import os

class TeacherService:
    def __init__(self):
        self.enabled = os.getenv("AUTONOMY_ENABLE_TEACHER_SYNTHESIS", "true").lower() == "true"
        self.max_samples = int(os.getenv("AUTONOMY_TEACHER_MAX_SAMPLES", "5"))
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            from backend.services.llm_service import LLMService

            self._llm = LLMService()
        return self._llm

    def enrich_samples(self, samples: list[dict]):
        if not self.enabled:
            return []

        enriched = []
        for sample in samples[: self.max_samples]:
            candidate = self._revise_sample(sample)
            if candidate:
                enriched.append(candidate)
        return enriched

    def _revise_sample(self, sample: dict):
        prompt = self._prompt(sample)
        try:
            response = self.llm.generate(prompt)
        except Exception as exc:
            return {
                "input": sample["input"],
                "output": sample["output"],
                "source": "teacher_fallback",
                "teacher_model": self.llm.model,
                "notes": [f"Teacher synthesis failed: {exc}"],
            }

        parsed = self._parse_response(response)
        if not parsed:
            return None

        return {
            "input": sample["input"],
            "output": parsed["output"],
            "source": "teacher_synthetic",
            "teacher_model": self.llm.model,
            "notes": parsed.get("notes", []),
        }

    def _prompt(self, sample: dict):
        return f"""
You are improving a training sample for an assistant model.

Return JSON with this exact shape:
{{"output":"improved answer","notes":["short reason"]}}

Rules:
- Keep the answer grounded and concise
- Do not mention chain of thought
- Improve clarity, correctness, and usefulness
- Output JSON only

User:
{sample['input']}

Current answer:
{sample['output']}
"""

    def _parse_response(self, response: str):
        try:
            payload = json.loads(response.strip())
        except json.JSONDecodeError:
            return None

        output = str(payload.get("output", "")).strip()
        if not output:
            return None
        notes = payload.get("notes", [])
        if not isinstance(notes, list):
            notes = []
        return {
            "output": output,
            "notes": [str(note) for note in notes[:3]],
        }
