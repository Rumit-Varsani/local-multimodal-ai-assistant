#!/bin/bash

set -euo pipefail

PROJECT_PATH="${PROJECT_PATH:-$HOME/ai-project}"
VENV_PATH="${VENV_PATH:-$PROJECT_PATH/venv}"
HOST="${ASSISTANT_HOST:-0.0.0.0}"
PORT="${ASSISTANT_PORT:-8000}"

cd "$PROJECT_PATH"
source "$VENV_PATH/bin/activate"

echo "Starting FastAPI on $HOST:$PORT from $PROJECT_PATH"
exec uvicorn backend.main:app --host "$HOST" --port "$PORT"
