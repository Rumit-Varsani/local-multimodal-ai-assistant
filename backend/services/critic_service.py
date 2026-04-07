class CriticService:
    def score_sample(self, sample: dict):
        output = str(sample.get("output", "")).strip()
        notes = []
        score = 0.4

        if output:
            score += 0.2
        if len(output) >= 20:
            score += 0.1
        if len(output) <= 500:
            score += 0.1
        if sample.get("source") == "teacher_synthetic":
            score += 0.1
            notes.append("Sample was improved by the teacher model.")
        if "I don't have that information." in output:
            score += 0.05
            notes.append("Sample preserves uncertainty handling.")

        return {
            "score": round(min(score, 0.95), 2),
            "accepted": score >= 0.6,
            "notes": notes,
        }
