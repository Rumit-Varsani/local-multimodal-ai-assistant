class ProjectPhaseService:
    PHASES = [
        {
            "id": 1,
            "name": "Core Runtime",
            "status": "completed",
            "goal": "Single-node local runtime with chat, memory, Ollama, and stable Dell/Mac separation.",
            "includes": [
                "FastAPI backend",
                "Streamlit chat UI",
                "Dell runtime-only workflow",
                "memory and logging",
            ],
        },
        {
            "id": 2,
            "name": "Autonomy Foundation",
            "status": "completed",
            "goal": "Worker, queue, datasets, checkpoints, and live autonomy status.",
            "includes": [
                "background worker",
                "job queue",
                "dataset builder",
                "checkpoint scaffolding",
                "autonomy routes",
            ],
        },
        {
            "id": 3,
            "name": "Multi-Model Learning",
            "status": "in_progress",
            "goal": "Route across models, learn topics, track model choices, and show progress in the dashboard.",
            "includes": [
                "multi-model routing",
                "topic training",
                "SQLite memory",
                "training controls",
                "dashboard visibility",
            ],
        },
        {
            "id": 4,
            "name": "Evaluation and Ranking",
            "status": "pending",
            "goal": "Judge-style comparison, held-out evaluation, confidence scoring, and better answer ranking.",
            "includes": [
                "judge comparison",
                "confidence scores",
                "held-out eval set",
                "better ranking signals",
            ],
        },
        {
            "id": 5,
            "name": "Real Training Execution",
            "status": "pending",
            "goal": "Real LoRA or QLoRA jobs, safe execution, and hardware-aware training.",
            "includes": [
                "trainer execution",
                "hardware safeguards",
                "run recovery",
                "trainer metrics",
            ],
        },
        {
            "id": 6,
            "name": "Promotion Loop",
            "status": "pending",
            "goal": "Benchmark, promote, and rollback checkpoints safely.",
            "includes": [
                "promotion gates",
                "checkpoint comparison",
                "rollback state",
                "deployment safety",
            ],
        },
        {
            "id": 7,
            "name": "Fully Autonomous ForgeMind",
            "status": "pending",
            "goal": "Long-running self-improving learning, routing, training, and evaluation with minimal human input.",
            "includes": [
                "always-on learning",
                "continuous routing feedback",
                "automatic training cycles",
                "visible improvement over time",
            ],
        },
    ]

    def summary(self):
        current = next((phase for phase in self.PHASES if phase["status"] == "in_progress"), None)
        return {
            "current_phase": current,
            "completed_count": sum(1 for phase in self.PHASES if phase["status"] == "completed"),
            "total_count": len(self.PHASES),
            "phases": self.PHASES,
        }
