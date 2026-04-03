# backend/services/memory_service.py

from memory.memory import get_all_memories, search_memory, store_memory


class MemoryService:
    def retrieve(self, query: str):
        return search_memory(query)

    def retrieve_all(self):
        return get_all_memories()

    def store(self, text: str):
        store_memory(text)
