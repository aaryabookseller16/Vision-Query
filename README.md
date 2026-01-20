# VisionQuery

VisionQuery is a lightweight **text-to-image semantic search** system built as a backend-first MVP.

The project demonstrates how to:
- Serve a pretrained multimodal model via an API
- Index image embeddings
- Perform similarity search using cosine similarity
- Package and run everything reproducibly with Docker

The focus is on **clean system design and extensibility**, not building a large-scale production system.

## High-Level Overview

VisionQuery allows users to:
1. Ingest images into a search index
2. Query the system using natural language
3. Retrieve the most semantically similar images

Text and images are embedded into the **same vector space** using a pretrained CLIP model, enabling cross-modal search.

## Architecture

```
Client (curl / frontend)
↓
FastAPI Backend
↓
CLIP Embedder (text + image)
↓
In-Memory Vector Store (cosine similarity)
↓
Search Results
```

Key design choices:
- **FastAPI** for a simple, fast HTTP API
- **Pretrained CLIP** model (no custom training)
- **In-memory vector store** for clarity and easy iteration
- **Docker + Docker Compose** for reproducible runs

## Project Structure

```
visionquery/
├── backend/
│   ├── app/
│   │   ├── main.py          # API routes and orchestration
│   │   ├── embeddings.py    # Text + image embedding logic
│   │   └── vector_store.py  # In-memory similarity search
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── images/              # Local image data (not tracked)
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Health Check

**GET** `/health`

Returns:

```json
{ "status": "ok" }
```

### Ingest Image

**POST** `/ingest/image`

Body:

```json
{
  "path": "data/images/example.jpg"
}
```

Indexes the image by generating and storing its embedding.

### Search

**POST** `/search`

Body:

```json
{
  "query": "a red car on the street"
}
```

Returns the most semantically similar images with similarity scores.

## Running Locally (Recommended)

### Prerequisites
- Docker
- Docker Compose

### Start the backend

From the project root, run:

```bash
docker compose up --build
```

The API will be available at:

```
http://localhost:8000
```

## Development Notes

- The CLIP model is loaded once at startup to avoid per-request overhead.
- All embeddings live in memory for simplicity.
- The vector store is intentionally minimal and can be replaced later with FAISS, pgvector, or a managed vector database.

## Limitations (Intentional)

This project is an MVP and not production-hardened:
- No persistence layer (index resets on restart)
- No authentication
- No batching or async inference
- No frontend yet

These were conscious tradeoffs to prioritize clarity and correctness.

## Future Improvements

Possible next steps:
- Replace in-memory store with FAISS or pgvector
- Add persistent metadata storage
- Add a simple React frontend
- Improve observability and error handling
- Batch and async inference for better throughput

## Why This Project Exists

VisionQuery was built to practice:
- API design around ML models
- Clean separation of concerns
- Dockerized development workflows
- Explaining ML systems clearly and honestly

It is intentionally scoped to be easy to reason about and extend.