# backend/services/memory_service.py

from memory.memory import store_memory, search_memory


class MemoryService:
    def retrieve(self, query: str):
        return search_memory(query)

    def store(self, text: str):
        store_memory(text)