import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()

collection = client.create_collection(name="ai_memory")

model = SentenceTransformer("all-MiniLM-L6-v2")


def store_memory(text):

    embedding = model.encode(text).tolist()

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(hash(text))]
    )


def search_memory(query):

    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=3
    )

    return results["documents"]