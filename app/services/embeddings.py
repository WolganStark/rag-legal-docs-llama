import os
from typing import List
from sentence_transformers import SentenceTransformer
from app.config.settings import settings




class EmbeddingService:
    def __init__(self):
        self.provider = os.getenv("EMBEDDING_PROVIDER")
        self.model_name = os.getenv("EMBEDDING_MODEL")

        if not self.provider:
            raise RuntimeError("EMBEDDING_PROVIDER not set in .env")

        if not self.model_name:
            raise RuntimeError("EMBEDDING_MODEL not set in .env")

        if self.provider != "huggingface":
            raise ValueError(f"Unsupported embedding provider: {self.provider}")

        print(f"[EmbeddingService] Loading model: {self.model_name}")

        self.model = SentenceTransformer(self.model_name)

        print("[EmbeddingService] Model loaded successfully")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()

    def embed_query(self, query: str) -> List[float]:
        return self.model.encode(
            query,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()


if __name__ == "__main__":
    service = EmbeddingService()

    texts = [
        "Este es un documento legal sobre protección de datos.",
        "This document describes GDPR regulations."
    ]

    embeddings = service.embed_texts(texts)

    print(f"Number of embeddings: {len(embeddings)}")
    print(f"Embedding dimension: {len(embeddings[0])}")
