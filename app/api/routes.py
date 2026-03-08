from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import os

from app.core.container import Container
from app.config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["rag"])


class AskRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        description="Natural language question",
        example="¿Qué dice la ley colombiana sobre el trabajo nocturno?",
        openapi_examples={
            "laboral": {
                "summary": "Consulta laboral",
                "value": {"query": "¿Qué dice la ley colombiana sobre el trabajo nocturno?"},
            },
            "gdpr": {
                "summary": "Consulta GDPR",
                "value": {"query": "¿Cuáles son los derechos del titular de datos según el GDPR?"},
            },
            "despido": {
                "summary": "Despido injustificado",
                "value": {"query": "¿Qué indemnización corresponde por despido sin justa causa?"},
            },
        },
    )


class SourceItem(BaseModel):
    source: str | None = None
    score: float | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


class DocumentsResponse(BaseModel):
    documents: dict[str, list[str]]  # {"gdpr": ["archivo1.pdf"], "legal": [...]}


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/documents", response_model=DocumentsResponse)
def list_documents() -> DocumentsResponse:
    """
    Lista todos los PDFs disponibles agrupados por subcarpeta.
    Lee directamente el sistema de archivos del contenedor de la API,
    que es quien tiene acceso al volumen de documentos.
    """
    docs_path = os.getenv("DOCS_PATH", "./data/raw_documents")
    result: dict[str, list[str]] = {}

    try:
        for root, dirs, files in os.walk(docs_path):
            pdf_files = [f.replace(".pdf", "") for f in sorted(files) if f.endswith(".pdf")]
            if pdf_files:
                # Carpeta relativa como clave — ej: "gdpr", "legal", ""
                folder = os.path.relpath(root, docs_path)
                # "." significa que los PDFs están en la raíz de docs_path
                key = "" if folder == "." else folder
                result[key] = pdf_files
    except FileNotFoundError:
        pass

    return DocumentsResponse(documents=result)


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    try:
        rag = Container.get_rag()
        result = rag.ask(payload.query)
        return AskResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {exc}") from exc