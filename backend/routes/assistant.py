# backend/routes/assistant.py

from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from backend.agents.router_agent import RouterAgent

router = APIRouter()
router_agent = RouterAgent()


class AssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str


@router.post("/")
async def assistant(
    req: Optional[AssistantRequest] = Body(default=None),
    message: Optional[str] = Query(default=None),
    prompt: Optional[str] = Query(default=None),
):
    user_message = None

    if req is not None and req.message:
        user_message = req.message
    elif message:
        user_message = message.strip()
    elif prompt:
        user_message = prompt.strip()

    if not user_message:
        raise HTTPException(status_code=422, detail="Provide message in JSON body or message/prompt query parameter.")

    result = router_agent.route(message=user_message)
    return {"response": result}
