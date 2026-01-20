# VisionQuery

VisionQuery is a lightweight **text-to-image semantic search system** built as a backend-first MVP.  
It demonstrates how to serve a pretrained multimodal model behind an API, index image embeddings, and perform similarity search — all in a clean, containerized setup.

The project intentionally prioritizes **clarity, correctness, and explainability** over scale.

---

## What VisionQuery Does

VisionQuery allows users to:

1. **Ingest images** into an embedding index
2. **Query using natural language**
3. **Retrieve semantically similar images** ranked by similarity score

Both text and images are embedded into the **same vector space** using a pretrained CLIP model, enabling cross‑modal search without any custom training.

---

## High-Level Architecture

```
Client (curl / browser / frontend)
        ↓
FastAPI Backend
        ↓
CLIP Embedder (text + image)
        ↓
In-Memory Vector Store (cosine similarity)
        ↓
Ranked Search Results
```

### Key Design Choices
- **FastAPI** for a simple, fast HTTP API
- **Pretrained CLIP model** for multimodal embeddings
- **In-memory vector store** for simplicity and rapid iteration
- **Docker + Docker Compose** for reproducible local development
- **Lazy model loading** to ensure fast startup and reliable health checks

---

## Project Structure

```
visionquery/
├── backend/
│   ├── app/
│   │   ├── main.py          # API routes, orchestration, metrics
│   │   ├── embeddings.py    # Text + image embedding logic (CLIP)
│   │   └── vector_store.py  # In-memory similarity search
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # Simple React UI (optional)
├── data/
│   └── images/              # Local image data (not tracked)
├── monitoring/
│   └── prometheus/
│       └── prometheus.yml   # Prometheus scrape configuration
├── docker-compose.yml
└── README.md
```

---

## API Endpoints

### Health Check
**GET** `/health`

Used by Docker and monitoring tools to verify the service is running.

```json
{ "status": "ok" }
```

---

### Ingest Image
**POST** `/ingest/image`

Indexes an image by generating and storing its embedding.

```json
{
  "path": "data/images/example.jpg"
}
```

---

### Search
**POST** `/search`

Searches indexed images using a natural language query.

```json
{
  "query": "a red car on the street",
  "top_k": 5
}
```

Returns ranked results with similarity scores.

---

### Metrics
**GET** `/metrics`

Exposes Prometheus-compatible metrics for:
- Request counts
- Request latency

---

## Running the Project

### Prerequisites
- Docker
- Docker Compose

### Start All Services
From the project root:

```bash
docker compose up --build
```

### Available Services
- **Backend API:** http://localhost:8000  
- **Frontend UI:** http://localhost:5173  
- **Prometheus:** http://localhost:9090  
- **Grafana:** http://localhost:3000 (admin / admin)

---

## Observability

VisionQuery includes basic observability out of the box:

- **Prometheus** scrapes backend metrics
- **Grafana** visualizes request volume and latency
- Metrics are collected automatically via FastAPI middleware

This mirrors how production ML services are monitored in practice.

---

## Development Notes

- The CLIP model is **lazy-loaded** on first request to avoid slow container startup.
- Embeddings are stored in memory for simplicity.
- The vector store is intentionally minimal and easy to replace.

---

## Limitations (Intentional)

This project is an MVP and not production-hardened:

- No persistent storage (index resets on restart)
- No authentication or access control
- No batching or async inference
- No large-scale vector indexing

These were deliberate tradeoffs to keep the system easy to reason about and explain.

---

## Possible Extensions

- Replace in-memory store with FAISS or pgvector
- Add persistent metadata storage
- Improve frontend UX
- Add request tracing and error dashboards
- Batch or async inference for higher throughput

---

## Why This Project Exists

VisionQuery was built to practice and demonstrate:

- Designing clean APIs around ML models
- Structuring ML systems for reliability
- Containerized development workflows
- Adding observability to backend services
- Explaining ML infrastructure clearly in interviews

The scope is intentionally limited so every component can be understood end-to-end.