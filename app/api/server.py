from fastapi import FastAPI
import os
from app.api.routes import router
from app.config.settings import settings


def create_app() -> FastAPI:

    if settings.hf_token:
       os.environ["HF_TOKEN"] = settings.hf_token
    
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="RAG API for legal documents",
    )
    app.include_router(router)
    return app


app = create_app()
