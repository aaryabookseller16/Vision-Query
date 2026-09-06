from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.vector_store import VectorStore


class FakeEmbedder:
    def is_loaded(self):
        return True

    def embed_image(self, path: Path):
        return [1.0, 0.0] if "red" in path.name else [0.0, 1.0]

    def embed_text(self, text: str):
        return [1.0, 0.0] if "red" in text else [0.0, 1.0]


def setup_function():
    main.store = VectorStore()
    main.embedder = FakeEmbedder()


def test_health_is_lightweight():
    response = TestClient(main.app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True, "indexed_images": 0}


def test_ingest_and_search(monkeypatch, tmp_path):
    image = tmp_path / "red-car.jpg"
    image.write_bytes(b"fixture")
    monkeypatch.setenv("IMAGE_ROOT", str(tmp_path))
    client = TestClient(main.app)

    ingested = client.post("/ingest/image", json={"path": "red-car.jpg"})
    assert ingested.status_code == 201
    assert ingested.json()["indexed_images"] == 1

    result = client.post("/search", json={"query": "red vehicle", "top_k": 3})
    assert result.status_code == 200
    assert result.json()["results"][0]["path"] == "data/images/red-car.jpg"


def test_path_traversal_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv("IMAGE_ROOT", str(tmp_path))
    response = TestClient(main.app).post("/ingest/image", json={"path": "../secret.jpg"})
    assert response.status_code == 400


def test_missing_image_is_404(monkeypatch, tmp_path):
    monkeypatch.setenv("IMAGE_ROOT", str(tmp_path))
    response = TestClient(main.app).post("/ingest/image", json={"path": "missing.jpg"})
    assert response.status_code == 404


def test_request_validation():
    client = TestClient(main.app)
    assert client.post("/search", json={"query": " ", "top_k": 2}).status_code == 422
    assert client.post("/search", json={"query": "dog", "top_k": 21}).status_code == 422
