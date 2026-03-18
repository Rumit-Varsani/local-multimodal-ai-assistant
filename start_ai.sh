#!/bin/bash

echo "🚀 Starting AI Assistant..."

PROJECT_PATH="$HOME/ai-project"

# Kill old processes
pkill -f uvicorn
pkill -f main.py

# Open VS Code (reliable way)
open -a "Visual Studio Code" "$PROJECT_PATH"

# Wait for VS Code
sleep 5

# -----------------------------
# Terminal 1 → Ollama
# -----------------------------
osascript -e '
tell application "System Events"
    tell process "Code"
        keystroke "`" using {control down}
        delay 1
        keystroke "ollama serve"
        key code 36
    end tell
end tell
'

sleep 2

# -----------------------------
# Terminal 2 → ComfyUI
# -----------------------------
osascript -e '
tell application "System Events"
    tell process "Code"
        keystroke "`" using {control down}
        delay 1
        keystroke "cd ~/ai-project/ComfyUI && source ~/ai-project/venv/bin/activate && python3 main.py"
        key code 36
    end tell
end tell
'

sleep 2

# -----------------------------
# Terminal 3 → FastAPI
# -----------------------------
osascript -e '
tell application "System Events"
    tell process "Code"
        keystroke "`" using {control down}
        delay 1
        keystroke "cd ~/ai-project && source ~/ai-project/venv/bin/activate && uvicorn backend.main:app --reload"
        key code 36
    end tell
end tell
'

sleep 5

# Open browser
open http://127.0.0.1:8000/docs

echo "✅ All systems started!"