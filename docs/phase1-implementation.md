# Phase 1: Autonomous Training Pipeline - Implementation Plan

## Overview

**Goal**: Build the foundation for ForgeMind to improve itself without human intervention.

**Execution**: Run background workers on Dell that continuously collect data, generate training examples, evaluate outputs, and fine-tune a local model.

**Scope (Phase 1)**:
1. Job queue system
2. Background worker orchestration
3. Dataset builder (data collection + curation)
4. Training pipeline
5. Checkpoint management
6. Basic evaluation framework

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main FastAPI App                         │
│            (handles user chat requests)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────┐
        │  Job Queue (Redis/file-based) │
        │  - collect_data              │
        │  - generate_examples         │
        │  - evaluate_batch            │
        │  - fine_tune                 │
        │  - promote_checkpoint        │
        └──────────────────────────────┘
                     │
        ┌────────────┴────────────────┐
        ▼                             ▼
    ┌────────────────┐        ┌──────────────────┐
    │  Worker 1      │        │  Worker 2+       │
    │  (primary)     │        │  (optional scale)│
    │  - runs jobs   │        │  - runs jobs     │
    │  - one at time │        │  - parallel      │
    └────────────────┘        └──────────────────┘
        │                             │
        └────────────┬────────────────┘
                     │
        ┌────────────┴────────────────┐
        ▼                             ▼
    ┌─────────────┐          ┌────────────────┐
    │  Storage    │          │  External      │
    │  - models   │          │  Models        │
    │  - datasets │          │  - Ollama      │
    │  - logs     │          │  - teachers    │
    └─────────────┘          │  - evaluators  │
                             └────────────────┘
```

---

## Components to Build

### 1. Job Queue Service

**File**: `backend/services/job_queue_service.py`

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any

class JobType(Enum):
    COLLECT_DATA = "collect_data"
    GENERATE_EXAMPLES = "generate_examples"
    EVALUATE_BATCH = "evaluate_batch"
    FINE_TUNE = "fine_tune"
    PROMOTE_CHECKPOINT = "promote_checkpoint"

@dataclass
class Job:
    id: str
    job_type: JobType
    status: str  # "pending" | "running" | "completed" | "failed"
    payload: Dict[str, Any]
    result: Dict[str, Any] = None
    error: str = None
    created_at: str
    started_at: str = None
    completed_at: str = None
```

**Responsibilities**:
- Enqueue jobs (from user interactions, scheduler, manual triggers)
- Dequeue jobs for workers to claim
- Track job status (pending → running → completed/failed)
- Persist job history to JSONL
- Provide status API endpoints

**Storage**: File-backed queue (simpler than Redis for local setup)
- `storage/job_queue.jsonl`: all jobs with metadata
- `storage/job_queue_status.jsonl`: latest status snapshots

### 2. Background Worker

**File**: `backend/services/background_worker_service.py`

**Responsibilities**:
- Poll job queue for pending jobs
- Execute jobs (delegate to specialized handlers)
- Update job status as it progresses
- Handle failures gracefully (retry logic, error logging)
- Report completion

**Execution Model**:
- Runs as separate Python process/thread
- Can be launched from CLI or as a systemd service on Dell
- Should **not** block the main FastAPI app

```python
class BackgroundWorker:
    def run_forever(self):
        """Poll queue and process jobs indefinitely"""
        while True:
            job = self.queue.dequeue_next()
            if job:
                self.execute_job(job)
            else:
                time.sleep(5)  # backoff
    
    def execute_job(self, job):
        try:
            self.queue.mark_running(job.id)
            result = self.dispatch_handler(job)
            self.queue.mark_completed(job.id, result)
        except Exception as e:
            self.queue.mark_failed(job.id, str(e))
```

### 3. Dataset Builder

**File**: `backend/services/dataset_builder_service.py`

**Input**: Collected interactions (existing: `storage/interactions.jsonl`)

**Process**:
1. Read recent interactions
2. Extract training samples (user input → response pairs)
3. Score samples using evaluation service
4. Deduplicate similar samples (embedding-based)
5. Group into batches

**Output**: Structured datasets
- `storage/datasets/train_v1.jsonl`: high-quality examples
- `storage/datasets/raw_v1.jsonl`: all collected examples
- `storage/datasets/splits_v1.json`: train/test/val split metadata

**Job Type**: `GENERATE_EXAMPLES`
```json
{
  "id": "gen_ex_001",
  "job_type": "generate_examples",
  "status": "running",
  "payload": {
    "source": "interactions.jsonl",
    "min_score": 0.7,
    "dedup_threshold": 0.85
  },
  "started_at": "2026-04-07T10:30:00Z"
}
```

### 4. Training Pipeline

**File**: `backend/services/training_service.py`

**Responsibilities**:
- Load dataset
- Set up training environment (VRAM checks, model loading from Ollama)
- Run fine-tuning with LoRA or similar efficient technique
- Save checkpoint
- Log training metrics

**Job Type**: `FINE_TUNE`
```json
{
  "id": "ft_001",
  "job_type": "fine_tune",
  "payload": {
    "dataset": "train_v1",
    "model": "phi3:mini",
    "epochs": 1,
    "batch_size": 4,
    "learning_rate": 2e-4,
    "output_dir": "storage/checkpoints/ckpt_001"
  }
}
```

**Output**:
- Fine-tuned model weights
- Training log: `storage/training_logs/ft_001.jsonl`
- Metadata: `storage/checkpoints/ckpt_001/metadata.json`

### 5. Checkpoint Manager

**File**: `backend/services/checkpoint_service.py`

**Responsibilities**:
- Track checkpoint versions
- Load/save model weights
- Manage model registry (which checkpoint is "current", which is "promoted")
- Support rollback if needed

**Storage**:
```
storage/checkpoints/
├── ckpt_000/ (baseline Phi3)
│   ├── metadata.json
│   └── model.bin (or gguf)
├── ckpt_001/ (after training run 1)
│   ├── metadata.json
│   ├── model.bin
│   └── metrics.json (train loss, eval scores)
└── model_registry.json
```

**model_registry.json example**:
```json
{
  "current": "ckpt_000",
  "promoted": "ckpt_000",
  "candidates": ["ckpt_001"],
  "history": [
    {"ckpt": "ckpt_000", "avg_score": 0.75, "promoted_at": "2026-04-07"},
    {"ckpt": "ckpt_001", "avg_score": 0.78, "promoted_at": "2026-04-08"}
  ]
}
```

### 6. Evaluation Framework (Enhanced)

**File**: `backend/services/evaluation_service.py` (expand existing)

**Current**: Evaluates user responses
**New**: Evaluate training data and checkpoints

**Metrics**:
- Correctness (semantic/task-specific scoring)
- Usefulness (relevance to query)
- Brevity (token efficiency)
- Safety (refusal quality, harmful content check)
- Alignment (user preference match)

**Job Type**: `EVALUATE_BATCH`
```json
{
  "id": "eval_001",
  "job_type": "evaluate_batch",
  "payload": {
    "dataset": "raw_v1",
    "output_file": "evaluations_v1.jsonl"
  }
}
```

### 7. Training Scheduler (Optional Phase 1)

**File**: `backend/services/training_scheduler.py` (or config-based)

**Responsibilities**:
- Trigger training jobs on a schedule (e.g., nightly)
- Or trigger when certain conditions are met (new data threshold, evaluation scores)

**Config example** (`storage/training_config.json`):
```json
{
  "schedule": "daily",
  "min_new_interactions": 100,
  "min_avg_eval_score": 0.7,
  "max_concurrent_jobs": 1,
  "checkpoints_to_keep": 5
}
```

---

## Workflow: End-to-End

### Day 1: Collection Phase

```
User chat with ForgeMind
     ↓
New interaction logged → interactions.jsonl
     ↓
Job enqueued: COLLECT_DATA
     ↓
Worker processes (already done, interaction is collected)
```

### Day N: Generation Phase (nightly)

```
Trigger: Daily schedule OR manual
     ↓
Enqueue: GENERATE_EXAMPLES
     ↓
Worker reads interactions.jsonl
Filter by quality (eval score > 0.7)
Deduplicate (embeddings)
Output: train_v1.jsonl, metrics
     ↓
Job completed ✓
```

### Day N: Training Phase

```
Trigger: Manual OR "enough new data"
     ↓
Enqueue: FINE_TUNE
  payload: {
    "dataset": "train_v1",
    "model": "phi3:mini",
    "epochs": 1
  }
     ↓
Worker loads train_v1.jsonl
Worker loads Ollama model
Worker runs LoRA fine-tuning
Worker saves → storage/checkpoints/ckpt_001/
     ↓
Job completed ✓
```

### Day N: Evaluation Phase

```
Trigger: After FINE_TUNE completes
     ↓
Enqueue: EVALUATE_BATCH
  payload: {
    "checkpoint": "ckpt_001",
    "test_set": "test_v1"
  }
     ↓
Worker runs checkpoint against test_set
Scores each output (correctness, safety, etc.)
Outputs: metrics.json
     ↓
Decision: Is ckpt_001 better than ckpt_000?
If yes →
  Enqueue: PROMOTE_CHECKPOINT
  Update model_registry.json
  ckpt_001 becomes the new "current" model
     ↓
Else → Keep current, archive ckpt_001
```

---

## API Changes

### New Routes (in `backend/routes/training.py`)

```python
@router.post("/jobs/enqueue")
async def enqueue_job(job_type: str, payload: dict):
    """Manually trigger a training job"""
    job_id = await job_queue_service.enqueue(job_type, payload)
    return {"job_id": job_id}

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Check job status"""
    return job_queue_service.get_job(job_id)

@router.get("/jobs")
async def list_jobs(status: str = None, limit: int = 100):
    """List all jobs, optionally filtered by status"""
    return job_queue_service.list_jobs(status, limit)

@router.get("/model/current")
async def get_current_model():
    """Get currently active model info"""
    return checkpoint_service.get_current()

@router.get("/model/checkpoints")
async def list_checkpoints():
    """List all saved checkpoints and metrics"""
    return checkpoint_service.list_checkpoints()

@router.post("/model/promote")
async def promote_checkpoint(ckpt_id: str):
    """Manually promote a checkpoint"""
    return checkpoint_service.promote(ckpt_id)
```

### Extend `/assistant` endpoint

The existing `/assistant` endpoint should detect when a new checkpoint is promoted and automatically use it:

```python
# In backend/routes/assistant.py
current_model = checkpoint_service.get_current()
llm_response = await llm_service.generate(
    prompt=full_prompt,
    model=current_model["model_id"]  # now dynamic!
)
```

---

## File Structure (Phase 1)

```
backend/
├── services/
│   ├── job_queue_service.py         [NEW]
│   ├── background_worker_service.py [NEW]
│   ├── dataset_builder_service.py   [NEW]
│   ├── training_service.py          [NEW]
│   ├── checkpoint_service.py        [NEW]
│   ├── training_scheduler.py        [NEW - optional]
│   ├── evaluation_service.py        [EXTEND]
│   └── ... (existing)
├── routes/
│   ├── training.py                  [NEW]
│   └── ... (existing)
└── workers/
    └── background_worker_main.py    [NEW - entry point]

storage/
├── job_queue.jsonl                  [NEW - job history]
├── job_queue_status.jsonl           [NEW - latest job status]
├── checkpoints/                     [NEW]
│   ├── ckpt_000/
│   │   ├── metadata.json
│   │   └── model.bin (or gguf)
│   └── model_registry.json
├── datasets/                        [NEW]
│   ├── train_v1.jsonl
│   ├── raw_v1.jsonl
│   └── splits_v1.json
├── training_logs/                   [NEW]
│   └── ft_001.jsonl
├── training_config.json             [NEW - scheduler config]
└── ... (existing)

scripts/
├── run_background_worker.sh         [NEW - start worker]
└── ... (existing)

docs/
├── phase1-implementation.md         (this file)
└── ... (existing)
```

---

## Implementation Order

**Week 1: Foundation**
1. Job Queue Service (file-backed, JSONL storage)
2. Background Worker (polling loop, error handling)
3. Job status API endpoints

**Week 2: Data**
4. Dataset Builder Service (dedupe, filtering, batching)
5. Enhanced Evaluation (batch scoring)
6. Manual COLLECT_DATA and GENERATE_EXAMPLES jobs

**Week 3: Training**
7. Checkpoint Manager (storage, registry, versioning)
8. Training Service (LoRA fine-tuning)
9. Manual FINE_TUNE job (test on a subset)

**Week 4: Promotion**
10. Checkpoint promotion logic
11. Automatic benchmark (EVALUATE_BATCH → PROMOTE_CHECKPOINT)
12. Scheduler (optional: automatic nightly runs)

---

## Testing Strategy

### Unit Tests
- Job queue enqueue/dequeue
- Checkpoint registry logic
- Dataset deduplication

### Integration Tests
- Full job cycle: enqueue → running → completed
- Dataset generation from interactions
- Checkpoint promotion (old vs new)

### End-to-End Test (Manual)
1. Generate synthetic interactions (or use real user chats)
2. Run `GENERATE_EXAMPLES` job
3. Run `FINE_TUNE` job with toy dataset (1-2 examples)
4. Run `EVALUATE_BATCH` job
5. Verify checkpoint was promoted
6. Test `/assistant` uses new model

---

## Key Decisions (For Discussion)

1. **Queue Storage**: File-based (JSONL) vs Redis?
   - File-based: simpler, no new dependency, works locally
   - Redis: FIFO guarantees, better for scaling

2. **Fine-tuning Method**: LoRA vs Full vs Quantized?
   - LoRA: efficient, low VRAM, recommended for 7B-13B models
   - Full: expensive but maximum capability
   - Quantized: low precision, fast, may hurt quality

3. **Scheduler**: Cron-like vs Always-on Loop?
   - Cron: clean separation, separate systemd service
   - Always-on: simpler code, one process to manage

4. **Model Evaluation**: Automated score + Human review?
   - Automated: fast, objective
   - Human review: catches blind spots, expensive
   - Recommendation: Start automated, add human loop later

---

## Next Steps

1. ✅ Review this plan
2. ⬜ Choose decisions (see above)
3. ⬜ Start with Job Queue Service
4. ⬜ Set up background worker CLI
5. ⬜ Build dataset builder
6. ⬜ Test full cycle with dummy data
7. ⬜ Integrate with Ollama for real fine-tuning
8. ⬜ Deploy to Dell as systemd service
