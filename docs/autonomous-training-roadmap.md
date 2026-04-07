# Autonomous Training Roadmap

## Project Name

**ForgeMind**

Why this name:
- `Forge` fits continuous improvement and model building
- `Mind` fits the assistant and memory-driven architecture
- short, distinctive, and easy to use in UI labels

Suggested model ids:
- `forgemind-3b`
- `forgemind-7b`
- `forgemind-core`
- `forgemind-instruct`

## Goal

Turn this repo into an autonomous local AI system that:

- uses open-source models as workers, critics, teachers, and evaluators
- keeps collecting data while you are away
- improves a target model through repeated fine-tuning cycles
- evaluates itself before promoting a new checkpoint

## Important Reality Check

We should **not** try to use every open-source model on the market.

Instead, we should build a **multi-model training pipeline** where each model has a job:

- a base target model to become ForgeMind
- one or two teacher models for high-quality synthetic data
- one coder model for repo-aware code tasks
- one evaluator model for scoring and filtering
- one embedding model for memory, retrieval, and deduplication

This is much more realistic, cheaper, and easier to control.

## Recommended System Design

### 1. Target model

Start with one trainable open model as the student:

- `Qwen3-8B` or `Qwen3-14B` for a strong base
- fallback: `Llama-3.3-70B-Instruct` as a teacher, not the first local student
- smaller local experimentation: `OLMo 2 7B` or `Mistral Small`

### 2. Teacher models

Use stronger open models to generate and refine training data:

- reasoning/general teacher: Qwen3 family
- broad assistant teacher: Llama 3.3 family
- coding teacher: Devstral or a strong open code model
- multilingual teacher if needed: Aya family

### 3. Evaluator models

Use separate models to grade outputs:

- response quality
- factual grounding
- instruction following
- code correctness
- safety and refusal quality

Never let the same model generate and fully grade its own output.

### 4. Autonomous loop

The always-on loop should be:

1. collect tasks
2. generate candidate answers with multiple open models
3. critique and compare outputs
4. keep only high-scoring examples
5. build datasets
6. fine-tune ForgeMind
7. run benchmark and safety evaluation
8. promote checkpoint only if it beats the current model

## What the agents should do

### Data agent

- collects conversations, tasks, logs, and failures
- converts interactions into training samples
- deduplicates low-value data

### Teacher agent

- asks multiple open models to solve the same task
- stores best responses and chain-of-thought-free rationales

### Critic agent

- scores quality, safety, brevity, and grounding
- rejects weak or conflicting samples

### Trainer agent

- prepares datasets
- launches LoRA or full fine-tuning jobs
- tracks checkpoints and metrics

### Benchmark agent

- runs held-out eval sets
- compares current production model vs candidate checkpoint

### Promotion agent

- only deploys new ForgeMind checkpoint if metrics improve
- rolls back automatically on regression

## Training strategy

### Phase 1

Do **LoRA / QLoRA instruction tuning** first.

This is the safest starting point for this repo because:

- cheaper than full pretraining
- works with smaller hardware
- enough to specialize the assistant
- good fit for your current chat and memory system

### Phase 2

Add preference optimization and self-improvement:

- pairwise ranking datasets
- critique/revision loops
- direct preference optimization

### Phase 3

Add long-running autonomy:

- scheduled jobs
- queue-based workers
- automatic dataset refresh
- nightly evaluation and training

### Phase 4

Only later consider continued pretraining if you have:

- massive clean corpus
- strong hardware budget
- reproducible evaluation
- checkpoint management

## Recommended first implementation in this repo

### New backend modules

- `backend/services/model_registry.py`
- `backend/services/task_queue_service.py`
- `backend/services/dataset_builder_service.py`
- `backend/services/training_service.py`
- `backend/services/benchmark_service.py`
- `backend/services/checkpoint_registry_service.py`
- `backend/agents/teacher_agent.py`
- `backend/agents/critic_agent.py`
- `backend/agents/trainer_agent.py`
- `backend/agents/autonomy_agent.py`

### New storage layout

- `storage/datasets/raw/`
- `storage/datasets/filtered/`
- `storage/checkpoints/`
- `storage/evals/`
- `storage/jobs/`

### New runtime flow

- FastAPI remains the serving layer
- a background worker loop runs autonomous jobs
- training and evaluation happen outside the chat request path

## Safety rules for self-improving systems

- never auto-promote a checkpoint without benchmark gating
- do not train directly on every conversation
- filter unsafe, low-quality, and contradictory examples
- keep golden evaluation sets that the model never trains on
- log every dataset, model source, and checkpoint used

## Best first model mix

If we build this now, a practical stack is:

- student: `Qwen3-8B`
- general teacher: `Qwen3-32B` or stronger available Qwen3 variant
- second teacher: `Llama-3.3-70B-Instruct`
- code teacher: `Devstral`
- multilingual teacher: `Aya` only if needed
- fully open research baseline: `OLMo`
- embeddings: a separate sentence-transformer or open embedding model

## First milestone

The first useful milestone is **not** training from scratch.

It is:

> Build ForgeMind as a self-improving assistant that can generate, critique, filter, fine-tune, and evaluate LoRA checkpoints automatically.

That milestone is realistic and can evolve into a much bigger system later.
