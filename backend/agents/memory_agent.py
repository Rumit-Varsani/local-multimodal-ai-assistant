# backend/agents/memory_agent.py

from backend.services.memory_service import MemoryService


class MemoryAgent:
    def __init__(self):
        self.memory = MemoryService()

    def get_context(self, query: str):
        memories = self.memory.retrieve(query)

        if not memories:
            return ""

        # 🔥 FILTER: only keep relevant memories
        relevant = []
        query_lower = query.lower()

        for mem in memories:
            if any(word in mem.lower() for word in query_lower.split()):
                relevant.append(mem)

        return "\n".join(relevant)

    def should_store(self, text: str):
        keywords = [
            "my name is",
            "i live",
            "i work",
            "i like",
            "i prefer"
        ]
        return any(k in text.lower() for k in keywords)

    def clean_memory(self, text: str):
        text_lower = text.lower()

        if "my name is" in text_lower:
            return f"User name is {text.split('is')[-1].strip()}"

        elif "i live" in text_lower:
            return f"User lives in {text.split('in')[-1].strip()}"

        elif "i work" in text_lower:
            return f"User works as {text.split('as')[-1].strip()}"

        elif "i like" in text_lower:
            return f"User likes {text.split('like')[-1].strip()}"

        return text.strip()

    def store_interaction(self, user_input: str, response: str):
        if self.should_store(user_input):
            clean = self.clean_memory(user_input)
            print("💾 Storing memory:", clean)
            self.memory.store(clean)