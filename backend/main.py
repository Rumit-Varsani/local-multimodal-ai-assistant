# backend/main.py

from fastapi import FastAPI
from backend.routes import assistant, autonomy, chat
from backend.runtime import autonomy_agent

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
app.include_router(autonomy.router, prefix="/autonomy")
app.include_router(chat.router, prefix="/chat")  # temporary fallback


@app.on_event("startup")
def startup():
    autonomy_agent.refresh_config_from_env()
    if autonomy_agent.auto_start:
        autonomy_agent.start()


@app.on_event("shutdown")
def shutdown():
    autonomy_agent.stop()
