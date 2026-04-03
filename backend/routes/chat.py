# backend/routes/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from backend.agents.router_agent import RouterAgent

router = APIRouter()
router_agent = RouterAgent()


class ChatRequest(BaseModel):
    prompt: str


@router.post("/")
def chat(req: ChatRequest):
    return {
        "response": router_agent.route(message=req.prompt)
    }