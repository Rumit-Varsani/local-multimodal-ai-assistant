# ForgeMind Master Phase Plan

## Phase 1: Core Runtime

Goal:
- Run ForgeMind locally with chat, Ollama, memory, and a stable Dell/Mac workflow.

Status:
- Completed

## Phase 2: Autonomy Foundation

Goal:
- Add the background worker, queue, dataset builder, checkpoint scaffolding, and runtime automation APIs.

Status:
- Completed

## Phase 3: Multi-Model Learning

Goal:
- Add multi-model routing, topic training, SQLite learning memory, model tracking, and dashboard controls.

Status:
- In progress

Implemented so far:
- multi-model candidate selection
- topic-training queueing
- SQLite memory for topics and model decisions
- model/resource visibility
- direct training controls in the dashboard
- training-run tracking

Still missing inside this phase:
- stronger model-vs-model ranking
- better routing feedback from real results
- clearer long-term progress metrics

## Phase 4: Evaluation and Ranking

Goal:
- Judge-style evaluation, held-out benchmarks, confidence scoring, and better ranking quality.

Status:
- Pending

## Phase 5: Real Training Execution

Goal:
- Real LoRA or QLoRA jobs, hardware-aware execution, and reliable run handling.

Status:
- Pending

## Phase 6: Promotion Loop

Goal:
- Promote better checkpoints safely, compare against baselines, and preserve rollback paths.

Status:
- Pending

## Phase 7: Fully Autonomous ForgeMind

Goal:
- Keep learning, training, evaluating, and improving with minimal human input.

Status:
- Pending

## Current Exact Project Phase

ForgeMind is currently in:

**Phase 3: Multi-Model Learning**

Reason:
- the runtime and autonomy base are already built
- topic training already exists
- multi-model routing has already started
- dashboard visibility already exists
- but stronger ranking, real training execution, and safe promotion loops are not finished yet
