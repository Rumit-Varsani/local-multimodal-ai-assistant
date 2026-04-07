class BenchmarkService:
    def evaluate_dataset(self, dataset: dict):
        sample_count = dataset.get("filtered_samples", 0)
        teacher_samples = dataset.get("teacher_samples", 0)
        quality = 0.2
        notes = []

        if sample_count >= 10:
            quality = 0.5
            notes.append("Dataset has enough samples for a small Phase 1 training cycle.")
        if sample_count >= 30:
            quality = 0.7
            notes.append("Dataset size supports a stronger LoRA-style checkpoint candidate.")
        if sample_count >= 75:
            quality = 0.85
            notes.append("Dataset is large enough for a meaningful autonomous checkpoint iteration.")
        if teacher_samples > 0:
            quality += 0.05
            notes.append("Teacher-synthesized samples improved dataset coverage.")

        return {
            "kind": "dataset",
            "score": round(min(quality, 0.95), 2),
            "sample_count": sample_count,
            "teacher_samples": teacher_samples,
            "ready_for_training": sample_count >= 10,
            "notes": notes,
        }

    def evaluate_checkpoint(self, *, checkpoint: dict, current_promoted: dict | None):
        candidate_score = checkpoint.get("benchmark", {}).get("score", 0.0)
        baseline_score = 0.0
        if current_promoted is not None:
            baseline_score = current_promoted.get("benchmark", {}).get("score", 0.0)

        should_promote = candidate_score >= max(0.6, baseline_score)
        notes = []
        if should_promote:
            notes.append("Candidate meets the minimum benchmark gate.")
        else:
            notes.append("Candidate did not beat the benchmark gate.")

        return {
            "kind": "checkpoint",
            "candidate_score": candidate_score,
            "baseline_score": baseline_score,
            "should_promote": should_promote,
            "notes": notes,
        }
