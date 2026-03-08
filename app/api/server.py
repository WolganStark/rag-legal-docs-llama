import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.config.settings import settings
from app.core.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup: se ejecuta al arrancar el servidor ──
    # Fuerza la carga del modelo de embeddings y el cliente de Chroma
    # antes de recibir cualquier request
    Container.get_rag()
    yield
    # ── Shutdown: se ejecutaría aquí al apagar el servidor ──


def create_app() -> FastAPI:
    if settings.hf_token:
        os.environ["HF_TOKEN"] = settings.hf_token

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="RAG API for legal documents",
        lifespan=lifespan,  # ← registra el evento de startup
    )
    app.include_router(router)
    return app


app = create_app()