from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.chat_agent import ChatAgent

router = APIRouter()

chat_agent = ChatAgent()


class ChatRequest(BaseModel):
    message: str


@router.post("/")
def chat(request: ChatRequest):

    response = chat_agent.run(request.message)

    return {"response": response}