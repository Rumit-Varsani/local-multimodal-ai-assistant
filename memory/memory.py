import hashlib
import time
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# Initialize Chroma client
STORAGE_PATH = Path("storage/chroma")
STORAGE_PATH.mkdir(parents=True, exist_ok=True)
client = chromadb.PersistentClient(path=str(STORAGE_PATH))

# Get or create collection (IMPORTANT: avoids crash on restart)
collection = client.get_or_create_collection(name="ai_memory")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------
# STORE MEMORY
# -----------------------------
def store_memory(text: str):
    try:
        embedding = model.encode(text).tolist()
        memory_id = hashlib.sha256(text.encode("utf-8")).hexdigest()

        collection.upsert(
            documents=[text],
            embeddings=[embedding],
            ids=[memory_id],
            metadatas=[{"timestamp": time.time()}]
        )

        print(f"✅ Stored memory: {text}")

    except Exception as e:
        print(f"❌ Memory store error: {e}")


# -----------------------------
# SEARCH MEMORY
# -----------------------------
def search_memory(query: str, n_results: int = 3):
    try:
        embedding = model.encode(query).tolist()  # ✅ FIXED

        results = collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )

        documents = results.get("documents", [[]])[0]

        print(f"🔍 Memory search for: {query}")
        print(f"📚 Found: {documents}")

        return documents

    except Exception as e:
        print(f"❌ Memory search error: {e}")
        return []


def get_all_memories(limit: int = 100):
    try:
        results = collection.get(limit=limit, include=["documents"])
        documents = results.get("documents", [])

        print(f"📦 Loaded all memories: {documents}")

        return documents
    except Exception as e:
        print(f"❌ Load all memories error: {e}")
        return []
