# backend/agents/router_agent.py

from backend.agents.chat_agent import ChatAgent


class RouterAgent:
    def __init__(self):
        self.chat_agent = ChatAgent()

    def route(self, message: str = None):
        return self.chat_agent.run(message)