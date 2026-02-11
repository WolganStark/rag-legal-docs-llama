import os
import uuid
from typing import List
from pathlib import Path

from langchain_core.documents import Document

from app.rag.ingest import load_all_pdfs
from app.rag.chroma_client import ChromaClient
from app.rag.embeddings import EmbeddingService
from app.config import CHROMA_COLLECTION

rebuild = os.getenv("REBUILD_INDEX", "false").lower() == "true"


def index_documents(
    data_dir: Path,
    embedding_service: EmbeddingService,
    chroma_client: ChromaClient
) -> None:

    print("📥 Loading documents...")
    documents: List[Document] = load_all_pdfs(data_dir)

    if not documents:
        print("⚠ No documents found.")
        return

    print(f"✅ Loaded {len(documents)} chunks.")

    collection = chroma_client.get_or_create_collection(CHROMA_COLLECTION)

    print("🧠 Generating embeddings...")
    embeddings = embedding_service.embed_documents(
        [doc.page_content for doc in documents]
    )

    print("💾 Storing in Chroma...")

    collection.add(
        ids=[str(uuid.uuid4()) for _ in documents],
        documents=[doc.page_content for doc in documents],
        metadatas=[doc.metadata for doc in documents],
        embeddings=embeddings,
    )

    print(f"📊 Total documents in collection: {collection.count()}")



if __name__ == "__main__":

    embedding_service = EmbeddingService()
    chroma_client = ChromaClient()

    rebuild = os.getenv("REBUILD_INDEX", "false").lower() == "true"

    if rebuild:
        print("🧹 Rebuilding index...")
        try:
            chroma_client.client.delete_collection(CHROMA_COLLECTION)
        except:
            pass

    index_documents(Path("data/raw_documents/legal"), embedding_service, chroma_client)
    index_documents(Path("data/raw_documents/gdpr"), embedding_service, chroma_client)
    index_documents(Path("data/raw_documents/privacy"), embedding_service, chroma_client)
