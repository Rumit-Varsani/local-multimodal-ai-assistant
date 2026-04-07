#!/bin/bash

set -euo pipefail

PROJECT_PATH="${PROJECT_PATH:-$HOME/ai-project}"
VENV_PATH="${VENV_PATH:-$PROJECT_PATH/venv}"
STREAMLIT_HOST="${STREAMLIT_HOST:-0.0.0.0}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

cd "$PROJECT_PATH"

if [[ -f "$VENV_PATH/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$VENV_PATH/bin/activate"
elif [[ -f "$VENV_PATH/Scripts/activate" ]]; then
  # shellcheck disable=SC1091
  source "$VENV_PATH/Scripts/activate"
else
  echo "Could not find a virtualenv activate script under $VENV_PATH"
  exit 1
fi

echo "Starting Dell-hosted Streamlit on $STREAMLIT_HOST:$STREAMLIT_PORT"
echo "Streamlit will talk to ${ASSISTANT_API_URL:-http://127.0.0.1:8000/assistant}"
exec streamlit run ui/chat.py --server.address "$STREAMLIT_HOST" --server.port "$STREAMLIT_PORT"
