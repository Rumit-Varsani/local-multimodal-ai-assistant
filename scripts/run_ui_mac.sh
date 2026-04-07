#!/bin/bash

set -euo pipefail

PROJECT_PATH="${PROJECT_PATH:-$HOME/ai-project}"
VENV_PATH="${VENV_PATH:-$PROJECT_PATH/venv}"

cd "$PROJECT_PATH"
source "$VENV_PATH/bin/activate"

echo "Starting Streamlit UI against ${ASSISTANT_API_URL:-http://127.0.0.1:8000/assistant}"
exec streamlit run ui/chat.py
