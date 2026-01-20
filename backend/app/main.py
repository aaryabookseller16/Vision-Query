"""
VisionQuery API (FastAPI)

This module is the orchestration layer for the backend:
- Exposes HTTP endpoints (/health, /ingest/image, /search, /metrics)
- Delegates embedding work to app.embeddings.Embedder
- Stores/searches vectors via app.vector_store.VectorStore

Key production detail:
- The embedding model is *lazy-loaded* inside Embedder (so the web server can start fast).
- We expose Prometheus metrics so we can monitor request volume and latency in real time.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Local modules that handle embeddings and vector search logic
from app.embeddings import Embedder
from app.vector_store import VectorStore


# -----------------------------
# Prometheus metrics
# -----------------------------
# Total request count by HTTP method + endpoint path
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint"],
)

# Request latency in seconds by endpoint path
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)


# -----------------------------
# App setup
# -----------------------------
app = FastAPI(title="VisionQuery API")

# Allow the React dev server (and local browser) to call the API.
# For production, you'll typically tighten this to your deployed domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The Embedder is responsible for turning images/text into vectors.
# It should not block server startup (model is lazy-loaded inside Embedder).
embedder = Embedder()

# In-memory vector store for similarity search.
# This can be swapped for FAISS / pgvector / a managed vector DB later.
store = VectorStore()


# -----------------------------
# Middleware: measure every request
# -----------------------------
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """
    Capture request count + latency for every endpoint.

    We label metrics by raw URL path (e.g., '/search').
    If you later add dynamic paths (e.g., '/items/{id}'), consider normalizing labels
    to avoid high-cardinality metrics.
    """
    endpoint = request.url.path
    start = time.perf_counter()

    try:
        response = await call_next(request)
        return response
    finally:
        elapsed = time.perf_counter() - start
        REQUEST_COUNT.labels(request.method, endpoint).inc()
        REQUEST_LATENCY.labels(endpoint).observe(elapsed)


# -----------------------------
# Routes
# -----------------------------
@app.get("/health")
def health() -> Dict[str, str]:
    """Lightweight health check endpoint used by Docker/compose and dev tools."""
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    """
    Prometheus scrape endpoint.
    Prometheus will GET this URL and ingest the exported metrics.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest/image")
def ingest_image(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest an image by:
      1) Validating the path exists
      2) Generating an image embedding
      3) Storing the embedding + minimal metadata in the vector store

    Payload example:
      { "path": "data/images/dog.jpg" }
    """
    image_path = payload.get("path")

    if not image_path:
        return {"error": "valid image path required"}

    # NOTE: This path is checked inside the container filesystem when running via Docker.
    if not os.path.exists(image_path):
        return {"error": f"image path not found: {image_path}"}

    vector = embedder.embed_image(image_path)
    store.add(vector, {"path": image_path})

    return {"status": "indexed", "path": image_path}


@app.post("/search")
def search(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Semantic search over indexed images using a text query.

    Payload example:
      { "query": "a dog", "top_k": 5 }
    """
    query = payload.get("query")
    top_k = int(payload.get("top_k", 5))

    if not query:
        return {"error": "query text required"}

    query_vector = embedder.embed_text(query)
    results = store.search(query_vector, top_k=top_k)

    return {
        "results": [{"path": meta["path"], "score": float(score)} for score, meta in results]
    }