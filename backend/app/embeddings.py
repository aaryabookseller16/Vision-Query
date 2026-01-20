"""
embeddings.py

Turns user inputs (text or images) into numeric vectors (embeddings) for similarity search.

Important design choice:
- We DO NOT download/load the CLIP model during API startup.
- Instead, we lazy-load it the first time an embedding is requested.

Why:
- Model download / initialization can take a while (especially in Docker).
- If we block startup, the container healthcheck fails and Docker marks it unhealthy.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Optional

from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor


@dataclass
class EmbedderConfig:
    """
    Configuration for the embedding model.

    You can swap the model name later (e.g., larger CLIP variants) without changing code.
    """
    model_name: str = "openai/clip-vit-base-patch32"


class Embedder:
    """
    Small wrapper around a pretrained CLIP model.

    CLIP produces embeddings in a shared vector space:
    - text and images live in the same space
    - enabling text-to-image (and image-to-image) similarity search
    """

    def __init__(self, config: Optional[EmbedderConfig] = None) -> None:
        self.config = config or EmbedderConfig()

        # Choose GPU if available, else CPU.
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Lazy-loaded objects (initialized on first request)
        self._model: Optional[CLIPModel] = None
        self._processor: Optional[CLIPProcessor] = None

        # Make loading thread-safe (important under concurrent requests)
        self._load_lock = Lock()

    def _ensure_loaded(self) -> None:
        """
        Ensure the model + processor are loaded exactly once.

        This method is intentionally called inside embed_* methods so that
        API startup is fast and Docker healthchecks can pass immediately.
        """
        if self._model is not None and self._processor is not None:
            return

        with self._load_lock:
            # Check again after acquiring the lock (double-checked locking)
            if self._model is not None and self._processor is not None:
                return

            # Load processor + model
            processor = CLIPProcessor.from_pretrained(self.config.model_name)
            model = CLIPModel.from_pretrained(self.config.model_name).to(self.device)
            model.eval()

            self._processor = processor
            self._model = model

    def embed_text(self, text: str) -> list[float]:
        """
        Convert a text query into a vector embedding.

        Args:
            text: user query like "a red car on the street"

        Returns:
            A list[float] representing the embedding vector.
        """
        self._ensure_loaded()
        assert self._model is not None and self._processor is not None

        # Convert raw text into tensors the model understands
        inputs = self._processor(text=[text], return_tensors="pt", padding=True)

        # Move tensors to the same device as the model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Disable gradient tracking for faster inference
        with torch.no_grad():
            features = self._model.get_text_features(**inputs)

        # features shape: (1, D). Return the single vector.
        return features[0].cpu().tolist()

    def embed_image(self, image_path: str) -> list[float]:
        """
        Convert an image file into a vector embedding.

        Args:
            image_path: path to an image on disk

        Returns:
            A list[float] representing the embedding vector.
        """
        self._ensure_loaded()
        assert self._model is not None and self._processor is not None

        # Load image and standardize to RGB (avoids issues with grayscale/alpha images)
        image = Image.open(image_path).convert("RGB")

        # Convert image to model inputs (resize/normalize handled internally)
        inputs = self._processor(images=image, return_tensors="pt")

        # Move tensors to the same device as the model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Disable gradient tracking for faster inference
        with torch.no_grad():
            features = self._model.get_image_features(**inputs)

        # features shape: (1, D). Return the single vector.
        return features[0].cpu().tolist()

    def is_loaded(self) -> bool:
        """
        Useful for /ready endpoints or debugging.
        """
        return self._model is not None and self._processor is not None