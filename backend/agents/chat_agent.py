from backend.services.llm_service import LLMService
from backend.agents.memory_agent import MemoryAgent


class ChatAgent:
    def __init__(self):
        self.llm = LLMService()
        self.memory = MemoryAgent()

    def run(self, message: str):
        if not message:
            return "Please provide a message."

        # -----------------------------
        # 1. GET MEMORY
        # -----------------------------
        try:
            memory_context = self.memory.get_context(message)
            context_block = memory_context if memory_context else "No relevant memory."
        except Exception as e:
            print("❌ Memory error:", e)
            context_block = "No relevant memory."

        print("🧠 MEMORY:", context_block)

        # -----------------------------
        # 2. BUILD PROMPT
        # -----------------------------
        full_prompt = f"""
You are a helpful AI assistant.

Rules:
- Answer naturally and concisely
- Do NOT mention you are an AI
- Keep responses short and clear
- If unsure, say: "I don't have that information."

Memory:
{context_block}

User:
{message}

Assistant:
"""

        # -----------------------------
        # 3. LLM CALL
        # -----------------------------
        try:
            response = self.llm.generate(full_prompt)
        except Exception as e:
            print("❌ LLM error:", e)
            return "Something went wrong while generating a response."

        # -----------------------------
        # 4. SAFETY GUARD (ANTI-HALLUCINATION)
        # -----------------------------
        question_lower = message.lower()

        unsafe_patterns = [
            "what's in my",
            "what is in my",
            "what do i have in",
            "what's inside my"
        ]

        if any(p in question_lower for p in unsafe_patterns):
            if context_block == "No relevant memory.":
                response = "I don't have that information."

        # -----------------------------
        # 5. CLEAN OUTPUT
        # -----------------------------
        if "<assistant>" in response.lower():
            response = response.split("<assistant>")[-1].strip()

        # -----------------------------
        # 6. STORE MEMORY
        # -----------------------------
        try:
            self.memory.store_interaction(message, response)
        except Exception as e:
            print("❌ Memory store error:", e)

        return response.strip()