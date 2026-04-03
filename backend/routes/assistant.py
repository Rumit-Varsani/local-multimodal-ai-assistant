# backend/routes/assistant.py

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from backend.agents.router_agent import RouterAgent

router = APIRouter()
router_agent = RouterAgent()


class AssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str


@router.post("/")
async def assistant(req: AssistantRequest):
    result = router_agent.route(message=req.message)
    return {"response": result}
