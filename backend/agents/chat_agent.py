from backend.services.llm_service import LLMService


class ChatAgent:

    def __init__(self):

        self.llm = LLMService()

    def run(self, message: str):

        response = self.llm.generate(message)

        return response