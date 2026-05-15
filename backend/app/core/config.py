from __future__ import annotations

from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), env_ignore_empty=True, extra="ignore")

    APP_NAME: str = "Private Knowledge Assistant"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    DEBUG: bool = False

    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_ALGORITHM: str = "HS256"
    PASSWORD_BCRYPT_ROUNDS: int = 12
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000,https://eswar-rag.vercel.app"

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "rag"
    POSTGRES_USER: str = "rag"
    POSTGRES_PASSWORD: str = "rag"
    DATABASE_URL: Optional[str] = None

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    DATA_DIR: str = "/data"
    UPLOAD_DIR: str = "/data/uploads"
    VECTOR_DIR: str = "/data/vectors"

    VECTOR_STORE: str = "chroma"
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION: str = "documents"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENV: Optional[str] = None
    PINECONE_INDEX: Optional[str] = None

    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_CACHE_TTL_SECONDS: int = 86400
    MAX_BATCH_EMBEDDINGS: int = 64
    EMBEDDING_TIMEOUT_SECONDS: int = 60
    VECTOR_STORE_TIMEOUT_SECONDS: int = 60
    OPENAI_REQUEST_TIMEOUT_SECONDS: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 120

    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_CONTEXT_CHUNKS: int = 6
    HYBRID_ALPHA: float = 0.7

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_MAX_RETRIES: int = 2
    MAX_TOKENS: int = 512
    TEMPERATURE: float = 0.2

    RATE_LIMIT_PER_MINUTE: int = 60

    ASYNC_PROCESSING: bool = True
    RQ_QUEUE_NAME: str = "rag-jobs"

    MAX_UPLOAD_MB: int = 20
    ALLOWED_FILE_TYPES: str = "pdf,docx,txt,csv"

    ENABLE_ANALYTICS: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"dev", "development"}:
                return True
        return value


settings = Settings()


def build_database_url() -> str:
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


def build_redis_url() -> str:
    if settings.REDIS_URL:
        return settings.REDIS_URL
    if settings.REDIS_PASSWORD:
        return (
            f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        )
    return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
