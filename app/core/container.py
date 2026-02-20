from app.services.embeddings import EmbeddingService
from app.vector_store.chroma_client import ChromaClient
from app.services.retriever import RetrieverService
from app.services.generator import OllamaGenerator
from app.core.rag_pipeline import RAGPipeline


class Container:

    _rag_instance = None

    @classmethod
    def get_rag(cls):

        if cls._rag_instance is None:

            embedding_service = EmbeddingService()
            chroma_client = ChromaClient()

            retriever = RetrieverService(
                embedding_service,
                chroma_client,
                top_k=3
            )

            generator = OllamaGenerator()

            cls._rag_instance = RAGPipeline(retriever, generator)

        return cls._rag_instance