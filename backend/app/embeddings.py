"""Lazy CLIP text and image embedding adapter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass(frozen=True)
class EmbedderConfig:
    model_name: str = "openai/clip-vit-base-patch32"


class Embedder:
    """Loads CLIP on first use so health checks remain fast."""

    def __init__(self, config: EmbedderConfig | None = None) -> None:
        self.config = config or EmbedderConfig()
        self.device = "cpu"
        self._model: Any | None = None
        self._processor: Any | None = None
        self._torch: Any | None = None
        self._load_lock = Lock()

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is not None:
                return
            import torch
            from transformers import CLIPModel, CLIPProcessor

            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self._processor = CLIPProcessor.from_pretrained(self.config.model_name)
            self._model = CLIPModel.from_pretrained(self.config.model_name).to(self.device)
            self._model.eval()
            self._torch = torch

    def embed_text(self, text: str) -> list[float]:
        self._ensure_loaded()
        assert self._model is not None and self._processor is not None and self._torch is not None
        inputs = {key: value.to(self.device) for key, value in self._processor(text=[text], return_tensors="pt", padding=True).items()}
        with self._torch.inference_mode():
            features = self._model.get_text_features(**inputs)
        return features[0].cpu().tolist()

    def embed_image(self, image_path: str | Path) -> list[float]:
        self._ensure_loaded()
        assert self._model is not None and self._processor is not None and self._torch is not None
        from PIL import Image

        with Image.open(image_path) as source:
            image = source.convert("RGB")
            inputs = {key: value.to(self.device) for key, value in self._processor(images=image, return_tensors="pt").items()}
        with self._torch.inference_mode():
            features = self._model.get_image_features(**inputs)
        return features[0].cpu().tolist()

    def is_loaded(self) -> bool:
        return self._model is not None
