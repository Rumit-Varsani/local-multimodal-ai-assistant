# ForgeMind

A local-first AI assistant with memory, evaluation, reflection, and a foundation for autonomous self-improvement.

## Current Architecture

User -> Streamlit UI -> FastAPI -> Chat Agent -> Memory + Ollama

## Current Components

- FastAPI backend
- Streamlit chat UI
- ChromaDB-backed memory
- file-backed brain state, evaluations, and interaction logs
- local Ollama model integration

## Recommended Runtime Split

- Dell laptop: Ollama, FastAPI, storage, future training jobs, future autonomy loop
- MacBook: coding, git, browser testing, optional Streamlit UI via SSH tunnel

See [remote-dev-setup.md](/Users/rumitvarsani/ai-project/docs/remote-dev-setup.md) for the recommended workflow.

## Notes

- The long-term autonomous training roadmap lives in [autonomous-training-roadmap.md](/Users/rumitvarsani/ai-project/docs/autonomous-training-roadmap.md).
- This project is currently text-first. Older multimodal/startup artifacts have been removed or replaced as part of the cleanup.
