# Phase 1 Progress

## Goal of Phase 1

Build the first autonomous improvement loop for ForgeMind.

Phase 1 is considered successful when the project can:

- collect interaction logs
- build training datasets automatically
- maintain a job queue
- run autonomous cycles in the background
- plan training work for the student model
- register candidate checkpoints
- promote checkpoints only after simple benchmark gating
- expose status through API routes

## What is implemented now

### Core autonomy services

- file-backed job queue
- dataset builder from interaction logs
- model registry for student and teacher roles
- teacher synthesis for dataset enrichment
- critic scoring for dataset filtering
- multi-model Ollama querying and fallback candidates
- SQLite-backed training topic and model-decision tracking
- training plan scaffolding
- training run records with executable command templates
- checkpoint registry
- benchmark gating

### Runtime automation

- background autonomy worker
- automatic idle autonomy-cycle enqueueing
- startup and shutdown integration with FastAPI
- environment-controlled teacher synthesis and training command generation

### API routes

- `GET /autonomy/status`
- `POST /autonomy/start`
- `POST /autonomy/stop`
- `POST /autonomy/run-once`
- `POST /autonomy/jobs/autonomy-cycle`
- `GET /autonomy/jobs`
- `GET /autonomy/checkpoints`
- `GET /training/topics`

## What Phase 1 does not do yet

Phase 1 is **not** full self-training from raw compute to deployed model weights without supervision.

It currently provides:

- autonomous orchestration
- artifact generation
- teacher-enriched dataset preparation
- checkpoint planning
- training-run preparation
- promotion bookkeeping
- topic-training command queuing

It does **not yet** provide:

- real LoRA execution
- GPU-aware trainer execution
- multi-model teacher orchestration across distinct open models
- held-out benchmark suites
- rollback-aware deployment automation
- smarter resource-aware routing feedback from real benchmark history

## Why this is still the right Phase 1

This phase makes the project operationally autonomous enough to:

- keep working while you are away
- create datasets from real usage
- plan repeatable training cycles
- track checkpoint history
- expose progress clearly through files and APIs

That gives us a stable base for the next phase instead of jumping straight into fragile training code.
