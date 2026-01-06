import httpx
import numpy as np
from typing import List, Optional
from app.core.config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.model = settings.embedding_model

    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text using Ollama."""
        if not text or not text.strip():
            return None

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text.strip()
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("embedding")
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    async def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for a batch of texts."""
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings

    def normalize_for_embedding(self, title: str, songwriter: str = "") -> str:
        """Create a combined text for embedding generation."""
        parts = []
        if title:
            parts.append(f"Title: {title}")
        if songwriter:
            parts.append(f"Songwriter: {songwriter}")
        return " | ".join(parts)

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if vec1 is None or vec2 is None:
            return 0.0

        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))
