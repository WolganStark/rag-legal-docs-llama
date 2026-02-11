# app/services/retriever.py

from typing import List
from langchain_core.documents import Document

from app.services.embeddings import EmbeddingService
from app.vector_store.chroma_client import ChromaClient
from app.config.settings import settings


class RetrieverService:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        chroma_client: ChromaClient,
        top_k: int = 5
    ):
        self.embedding_service = embedding_service
        self.collection = chroma_client.get_or_create_collection(
            settings.chroma_collection
        )
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Document]:
        """
        Performs similarity search and returns top K relevant documents.
        """

        # 1️⃣ Embed query
        query_embedding = self.embedding_service.embed_query(query)

        # 2️⃣ Query Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"]
        )

        documents = []

        for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            documents.append(
                Document(
                    page_content=doc,
                    metadata={
                        **metadata,
                        "score": 1 - distance  # cosine similarity
                    }
                )
            )

        return documents

if __name__ == "__main__":

    embedding_service = EmbeddingService()
    chroma_client = ChromaClient()

    retriever = RetrieverService(
        embedding_service,
        chroma_client,
        top_k=3
    )

    query = "¿Qué dice GDPR sobre protección de datos personales?"

    docs = retriever.retrieve(query)

    for i, d in enumerate(docs, 1):
        print(f"\nResult {i}")
        print("Score:", d.metadata["score"])
        print(d.page_content[:300])
