import chromadb
from sentence_transformers import SentenceTransformer
import time

# Initialize Chroma client
client = chromadb.Client()

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

        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[str(hash(text))],
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