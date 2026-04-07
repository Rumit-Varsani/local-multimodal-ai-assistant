# backend/agents/router_agent.py

from backend.agents.chat_agent import ChatAgent
from backend.runtime import model_manager, router_service, sqlite_memory, task_queue, topic_training_service


class RouterAgent:
    def __init__(self):
        self.chat_agent = ChatAgent()

    def route(self, message: str = None):
        route = router_service.classify(message or "")
        if route["kind"] == "topic_training":
            training = topic_training_service.enqueue_topic(message=message or "", task_queue=task_queue)
            return (
                f"ForgeMind started training on '{training['topic']}'. "
                f"Topic id: {training['topic_id']}. "
                f"Planned subtopics: {', '.join(training['subtopics'])}."
            )

        routing = model_manager.describe_routing(route["task_type"])
        result = self.chat_agent.run(message)
        sqlite_memory.record_model_decision(
            task_type=route["task_type"],
            selected_model=routing["candidates"][0] if routing["candidates"] else "unknown",
            candidates=routing["candidates"],
            status="ok",
        )
        return result
