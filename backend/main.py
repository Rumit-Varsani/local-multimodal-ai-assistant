# backend/main.py

from fastapi import FastAPI
from backend.routes import assistant, chat

app = FastAPI()


# -----------------------------
# ROOT
# -----------------------------
@app.get("/")
def home():
    return {"status": "AI server running 🚀"}


# -----------------------------
# ROUTES
# -----------------------------
app.include_router(assistant.router, prefix="/assistant")
app.include_router(chat.router, prefix="/chat")  # temporary fallback