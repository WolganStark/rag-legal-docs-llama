# app/rag/chroma_client.py

import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

load_dotenv()


class ChromaClient:
    def __init__(self):
        persist_path = os.getenv("VECTOR_DB_PATH")

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
