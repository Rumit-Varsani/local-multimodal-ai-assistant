#!/bin/bash

set -euo pipefail

PROJECT_PATH="${PROJECT_PATH:-$HOME/ai-project}"
VENV_PATH="${VENV_PATH:-$PROJECT_PATH/venv}"
HOST="${ASSISTANT_HOST:-0.0.0.0}"
PORT="${ASSISTANT_PORT:-8000}"

cd "$PROJECT_PATH"

if [[ -f "$VENV_PATH/bin/activate" ]]; then
  # Unix/macOS virtualenv
  # shellcheck disable=SC1091
  source "$VENV_PATH/bin/activate"
elif [[ -f "$VENV_PATH/Scripts/activate" ]]; then
  # Git Bash on Windows virtualenv
  # shellcheck disable=SC1091
  source "$VENV_PATH/Scripts/activate"
else
  echo "Could not find a virtualenv activate script under $VENV_PATH"
  exit 1
fi

echo "Starting FastAPI on $HOST:$PORT from $PROJECT_PATH"
exec uvicorn backend.main:app --host "$HOST" --port "$PORT"
