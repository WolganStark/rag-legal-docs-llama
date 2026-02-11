from app.ingest.ingest import load_all_pdfs
from langchain_core.documents import Document


def test_ingest_pipeline():
    docs = load_all_pdfs()

    assert len(docs) > 0, "No documents were ingested"

    doc = docs[0]

    assert isinstance(doc, Document)
    assert hasattr(doc, "page_content")
    assert hasattr(doc, "metadata")

    assert "source" in doc.metadata
    assert "jurisdiction" in doc.metadata
    assert "language" in doc.metadata

def test_metadata_not_empty():
    docs = load_all_pdfs()

    unknown_count = 0

    for doc in docs:
        assert doc.page_content.strip() != ""

        if doc.metadata["language"] == "Unknown":
            unknown_count += 1

    # regla de negocio: máximo 20% sin idioma
    assert unknown_count / len(docs) < 0.2
