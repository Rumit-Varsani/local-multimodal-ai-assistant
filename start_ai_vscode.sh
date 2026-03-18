#!/bin/bash

echo "🚀 Starting AI Assistant..."

PROJECT_PATH="$HOME/ai-project"
OLLAMA_PATH="/opt/homebrew/bin/ollama"

# Kill old processes (clean start)
pkill -f uvicorn

# -----------------------------
# 1️⃣ Open VS Code
# -----------------------------
open -a "Visual Studio Code" "$PROJECT_PATH"

sleep 2

# -----------------------------
# 2️⃣ Start Ollama
# -----------------------------
osascript -e "
tell application \"Terminal\"
    do script \"echo '🧠 OLLAMA SERVER' && $OLLAMA_PATH serve\"
end tell
"

sleep 2

# -----------------------------
# 3️⃣ Start ComfyUI
# -----------------------------
osascript -e "
tell application \"Terminal\"
    do script \"echo '🎨 COMFYUI SERVER' && cd $PROJECT_PATH/ComfyUI && $PROJECT_PATH/venv/bin/python3 main.py\"
end tell
"

sleep 3

# -----------------------------
# 4️⃣ Start FastAPI
# -----------------------------
osascript -e "
tell application \"Terminal\"
    do script \"echo '⚡ FASTAPI SERVER' && cd $PROJECT_PATH && $PROJECT_PATH/venv/bin/uvicorn backend.main:app --reload\"
end tell
"

sleep 5

# -----------------------------
# 5️⃣ Open Browser
# -----------------------------
open http://127.0.0.1:8000/docs

echo "✅ All systems started!"