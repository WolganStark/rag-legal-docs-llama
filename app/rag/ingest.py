"""
ingest.py

Pipeline de Ingesta para documentos legales.
Responsabilidades:
- Cargar PDFs desde data/raw_documents
- Extraer texto por página
- Aplicar chunking
- Enriquecer metadata
"""

from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


DATA_DIR = Path("data/raw_documents")

def detect_metadata(filename: str) -> dict:
    filename_lower = filename.lower()

    if "colombia" in filename_lower:
        return {
            "jurisdiction": "Colombia",
            "document_type": "labor_law",
            "language": "es"
        }

    if "estatuto" in filename_lower:
        return {
            "jurisdiction": "Spain",
            "document_type": "labor_law",
            "language": "es"
        }

    if "gdpr" in filename_lower:
        return {
            "jurisdiction": "EU",
            "document_type": "regulation",
            "language": "en"
        }

    return {
        "jurisdiction": "Unknown",
        "document_type": "Unknown",
        "language": "Unknown"
    }


def load_all_pdfs() -> list[Document]:
    documents = []

    for pdf_path in DATA_DIR.glob("*.pdf"):
        try:
            loader = PyMuPDFLoader(str(pdf_path))
            docs = loader.load()

            semantic_metadata = detect_metadata(pdf_path.name)

            for d in docs:
                d.metadata.update({
                    "source": pdf_path.name,
                    **semantic_metadata
                })

            documents.extend(docs)

        except Exception as e:
            print(f"Error al procesar {pdf_path.name}: {e}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    return splitter.split_documents(documents)
