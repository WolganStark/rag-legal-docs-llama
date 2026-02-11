# app/vector_store/chroma_client.py

import chromadb
from chromadb.config import Settings
from app.config.settings import settings



class ChromaClient:
    def __init__(self):
        persist_path = settings.vector_db_path

        if not persist_path:
            raise RuntimeError("VECTOR_DB_PATH not set in .env")

        self.client = chromadb.PersistentClient(
            path=persist_path
        )

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}
        )
