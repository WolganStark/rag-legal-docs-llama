from app.services.embeddings import EmbeddingService
from app.vector_store.chroma_client import ChromaClient
from app.services.retriever import RetrieverService
from app.services.generator import OllamaGenerator
from app.core.rag_pipeline import RAGPipeline


if __name__ == "__main__":

    embedding_service = EmbeddingService()
    chroma_client = ChromaClient()

    retriever = RetrieverService(
        embedding_service,
        chroma_client,
        top_k=3
    )

    generator = OllamaGenerator()

    rag = RAGPipeline(retriever, generator)

    query = "¿Qué dice la ley Colombiana sobre el trabajo nocturno?"

    result = rag.ask(query)

    print("\nANSWER:\n")
    print(result["answer"])

    print("\nSOURCES:\n")
    for s in result["sources"]:
        print(s)
