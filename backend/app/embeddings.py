"""
embeddings.py

This file is responsible for turning user inputs (text or images) into numeric vectors
(embeddings) that can be compared using similarity search.

What this file does:
- Loads a pretrained CLIP model once (at startup)
- Provides two simple methods:
    - embed_text(text)  -> vector
    - embed_image(path) -> vector

Why we do it this way:
- Loading the model for every request would be extremely slow.
- Keeping it in memory makes the API responsive.
- This wrapper keeps ML details out of main.py so the API layer stays clean.
"""

from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor


class Embedder:
    """
    Small wrapper around a pretrained CLIP model.

    CLIP produces embeddings in a shared space:
    - text and images live in the same vector space
    - this lets us do text-to-image search with cosine similarity
    """

    def __init__(self):
        # Use GPU if available, otherwise fall back to CPU.
        # This keeps the code portable (works on laptops and servers).
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load model + processor once.
        #
        # Model: produces embeddings
        # Processor: handles tokenization for text and preprocessing for images
        #
        # NOTE: This is a pretrained model (we are not training anything here).
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        # Put the model in eval mode to disable training-only behavior (dropout etc.)
        self.model.eval()

    def embed_text(self, text: str):
        """
        Convert a text query into a vector embedding.

        Args:
            text: user query like "a red car on the street"

        Returns:
            A Python list of floats representing the embedding vector.
        """
        # Convert raw text into tensors the model understands
        inputs = self.processor(text=[text], return_tensors="pt", padding=True)

        # Move tensors to the same device as the model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Disable gradient tracking for faster inference
        with torch.no_grad():
            features = self.model.get_text_features(**inputs)

        # features shape: (1, D). We return the single vector as a list.
        return features[0].cpu().tolist()

    def embed_image(self, image_path: str):
        """
        Convert an image file into a vector embedding.

        Args:
            image_path: path to an image on disk

        Returns:
            A Python list of floats representing the embedding vector.
        """
        # Load image and standardize to RGB (avoids issues with grayscale/alpha images)
        image = Image.open(image_path).convert("RGB")

        # Convert image to model inputs (resize/normalize/etc handled internally)
        inputs = self.processor(images=image, return_tensors="pt")

        # Move tensors to the same device as the model
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Disable gradient tracking for faster inference
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)

        # features shape: (1, D). We return the single vector as a list.
        return features[0].cpu().tolist()