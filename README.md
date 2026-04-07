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
- Phase 1 autonomy worker, queue, dataset builder, and checkpoint scaffolding

## Recommended Runtime Split

- Dell laptop: Ollama, FastAPI, storage, future training jobs, future autonomy loop
- Dell laptop can also host Streamlit so you can open the full UI from your Mac browser using the Dell IP
- MacBook: coding, git, and browser/client access only

See [remote-dev-setup.md](/Users/rumitvarsani/ai-project/docs/remote-dev-setup.md) for the recommended workflow.

## Notes

- The long-term autonomous training roadmap lives in [autonomous-training-roadmap.md](/Users/rumitvarsani/ai-project/docs/autonomous-training-roadmap.md).
- The full project phase breakdown lives in [master-phase-plan.md](/Users/rumitvarsani/ai-project/docs/master-phase-plan.md).
- Current implementation progress lives in [phase1-progress.md](/Users/rumitvarsani/ai-project/docs/phase1-progress.md).
- The automated Mac-to-GitHub and Dell runtime workflow lives in [automated-workflow.md](/Users/rumitvarsani/ai-project/docs/automated-workflow.md).
- The simplest human-readable version lives in [simple-mac-dell-workflow.md](/Users/rumitvarsani/ai-project/docs/simple-mac-dell-workflow.md).
- Local git safety guards for Mac and Dell live in [git-guards.md](/Users/rumitvarsani/ai-project/docs/git-guards.md).
- Windows-specific Dell runtime notes live in [windows-dell-runtime.md](/Users/rumitvarsani/ai-project/docs/windows-dell-runtime.md).
- This project is currently text-first. Older multimodal/startup artifacts have been removed or replaced as part of the cleanup.
