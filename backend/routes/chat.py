# backend/routes/chat.py

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from backend.agents.router_agent import RouterAgent

router = APIRouter()
router_agent = RouterAgent()


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    prompt: str


@router.post("/")
def chat(req: ChatRequest):
    return {
        "response": router_agent.route(message=req.prompt)
    }
