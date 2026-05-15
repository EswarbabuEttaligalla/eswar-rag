from __future__ import annotations

from langchain_openai import OpenAIEmbeddings  # type: ignore[import-not-found]

from app.core.config import settings

_client: OpenAIEmbeddings | None = None


def get_embeddings() -> OpenAIEmbeddings:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY not configured")
        _client = OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
            max_retries=settings.OPENAI_MAX_RETRIES,
            timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS,
        )
    return _client