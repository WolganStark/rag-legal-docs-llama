from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.container import Container

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


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    try:
        rag = Container.get_rag()
        result = rag.ask(payload.query)
        return AskResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG pipeline error: {exc}") from exc
