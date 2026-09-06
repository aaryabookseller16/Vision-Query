"""VisionQuery FastAPI orchestration and observability layer."""

from __future__ import annotations

import os
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from app.embeddings import Embedder
from app.vector_store import VectorStore

REQUEST_COUNT = Counter("visionquery_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("visionquery_http_request_latency_seconds", "HTTP request latency", ["endpoint"])


class ImageIngestRequest(BaseModel):
    path: str = Field(min_length=1, max_length=512)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)


app = FastAPI(title="VisionQuery API", version="1.0.0")
origins = [item.strip() for item in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost").split(",") if item.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

embedder = Embedder()
store = VectorStore()
default_image_root = Path(__file__).resolve().parents[2] / "data" / "images"


def image_root() -> Path:
    return Path(os.getenv("IMAGE_ROOT", str(default_image_root))).expanduser().resolve()


def resolve_image_path(raw_path: str) -> Path:
    root = image_root()
    requested = Path(raw_path)
    if requested.is_absolute():
        candidate = requested.resolve()
    else:
        parts = requested.parts
        relative = Path(*parts[2:]) if len(parts) >= 2 and parts[:2] == ("data", "images") else requested
        candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="image path must stay inside the configured image directory")
    if not candidate.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="image not found")
    return candidate


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    endpoint = request.url.path
    start = time.perf_counter()
    response_status = 500
    try:
        response = await call_next(request)
        response_status = response.status_code
        return response
    finally:
        REQUEST_COUNT.labels(request.method, endpoint, str(response_status)).inc()
        REQUEST_LATENCY.labels(endpoint).observe(time.perf_counter() - start)


@app.get("/health")
def health() -> dict[str, object]:
    return {"status": "ok", "model_loaded": embedder.is_loaded(), "indexed_images": len(store)}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest/image", status_code=status.HTTP_201_CREATED)
def ingest_image(payload: ImageIngestRequest) -> dict[str, object]:
    path = resolve_image_path(payload.path)
    vector = embedder.embed_image(path)
    public_path = f"data/images/{path.relative_to(image_root()).as_posix()}"
    store.add(public_path, vector)
    return {"status": "indexed", "path": public_path, "indexed_images": len(store)}


@app.post("/search")
def search(payload: SearchRequest) -> dict[str, object]:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="query cannot be blank")
    results = store.search(embedder.embed_text(query), top_k=payload.top_k)
    return {"query": query, "results": [{"path": result.path, "score": result.score} for result in results]}
