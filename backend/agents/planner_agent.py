from backend.agents.chat_agent import run_chat_agent
from backend.agents.vision_agent import run_vision_agent

def run_planner(prompt):

    prompt_lower = prompt.lower()

    if "image" in prompt_lower or "photo" in prompt_lower:
        return "Please upload an image first."

    return run_chat_agent(prompt)