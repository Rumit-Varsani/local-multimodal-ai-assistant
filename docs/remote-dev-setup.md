# Remote Development Setup

## Goal

Use the Dell laptop as the only heavy runtime machine.

The Dell should handle:

- Ollama
- embeddings
- ChromaDB persistence
- FastAPI backend
- future training jobs
- future autonomous background workers

The MacBook should handle:

- editing code
- git operations
- lightweight UI usage
- browser testing
- SSH access to the Dell

## Recommended Topology

### Dell laptop

Run:

- `ollama serve`
- `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- future trainer / autonomy worker

Store:

- `storage/`
- model files
- datasets
- checkpoints

### MacBook

Do not run:

- Ollama
- embedding generation for production
- long training jobs
- background self-improvement loops

Use the Mac only to:

- edit the repo
- commit changes
- open Streamlit locally if needed
- connect to the Dell API over SSH tunnel or LAN

## Best connection method

Use an SSH tunnel from the Mac to the Dell:

```bash
ssh -N -L 8000:127.0.0.1:8000 <user>@<dell-host>
```

Then on the Mac:

- set `ASSISTANT_API_URL=http://127.0.0.1:8000/assistant`
- run the Streamlit UI locally if you want

This keeps the heavy backend on the Dell while the Mac talks to a local forwarded port.

## Branch workflow

Do not let both machines freely edit and push the same branch at the same time.

Recommended branches:

- `main`: stable branch
- `server/dell-runtime`: Dell-specific runtime and deployment changes
- `feature/<name>`: normal development work

Recommended workflow:

1. Make code changes on the Mac in `feature/<name>`.
2. Push to GitHub.
3. On the Dell, pull only when you are ready to update runtime.
4. Merge tested work into `main`.
5. Keep Dell-only operational tweaks in `server/dell-runtime` until they are ready for `main`.

## Important git rule

Each clone should stay on a predictable branch.

Suggested setup:

- Mac clone: active feature branch or `main`
- Dell clone: `server/dell-runtime` or a deployment branch

That prevents the Dell runtime copy from becoming a second development workspace that silently diverges.

## What should never happen

Your Mac should not accidentally start local Ollama, local backend, or local training when the Dell is supposed to do the work.

To avoid that:

- remove old Mac-only auto-launch scripts
- keep runtime launch scripts explicit
- rely on environment variables, not hardcoded local assumptions
