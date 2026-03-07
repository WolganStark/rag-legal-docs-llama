# app/config/settings.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str
    environment: str
    log_level: str

    # LLM
    llm_provider: str
    groq_api_key: str
    groq_model: str

    # Embeddings
    embedding_provider: str
    embedding_model: str

    # Vector DB
    vector_db: str
    vector_db_path: str
    chroma_collection: str

    # Chunking
    chunk_size: int
    chunk_overlap: int

    # Device
    device: str

    # Rebuild Index
    rebuild_index: bool = False

    # HuggingFace Hub
    hf_token: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()