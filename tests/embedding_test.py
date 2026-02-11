from app.services.embeddings import EmbeddingService


def test_embedding_service():
    service = EmbeddingService()

    texts = [
        "Documento legal en español",
        "Legal document in English"
    ]

    embeddings = service.embed_texts(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert isinstance(embeddings[0][0], float)
