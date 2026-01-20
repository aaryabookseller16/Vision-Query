from fastapi import FastAPI
import os

# Local modules that handle embeddings and vector search logic
from app.embeddings import Embedder
from app.vector_store import VectorStore

# Initialize the FastAPI application
# This file acts as the orchestration layer for the system
app = FastAPI(title="VisionQuery API")

# Load the embedding model once at startup
# This avoids reloading the model on every request, which would be expensive
embedder = Embedder()

# In-memory vector store for similarity search
# Designed to be easily replaceable with FAISS or a managed vector DB later
store = VectorStore()


@app.get("/health")
def health():
    """
    Lightweight health check endpoint.
    Used for development, monitoring, and container orchestration readiness checks.
    """
    return {"status": "ok"}


@app.post("/ingest/image")
def ingest_image(payload: dict):
    """
    Ingests an image into the system by:
    1. Validating the image path
    2. Generating an image embedding
    3. Storing the embedding with associated metadata

    This endpoint is intentionally simple and synchronous for MVP clarity.
    """
    image_path = payload.get("path")

    # Basic input validation
    if not image_path or not os.path.exists(image_path):
        return {"error": "valid image path required"}

    # Generate embedding for the image
    vector = embedder.embed_image(image_path)

    # Store vector along with minimal metadata
    store.add(vector, {"path": image_path})

    return {"status": "indexed", "path": image_path}


@app.post("/search")
def search(payload: dict):
    """
    Performs semantic search over indexed images using a text query.
    The query is embedded and compared against stored image embeddings
    using cosine similarity.
    """
    query = payload.get("query")

    if not query:
        return {"error": "query text required"}

    # Convert text query into an embedding
    query_vector = embedder.embed_text(query)

    # Perform similarity search against stored vectors
    results = store.search(query_vector)

    # Format results for API response
    return {
        "results": [
            {"path": meta["path"], "score": float(score)}
            for score, meta in results
        ]
    }