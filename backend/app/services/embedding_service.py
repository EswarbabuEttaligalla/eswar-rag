from __future__ import annotations

import asyncio
import hashlib
import logging

from app.embeddings.cache import EmbeddingCache
from app.embeddings.openai_embeddings import get_embeddings
from app.core.config import settings


logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.cache = EmbeddingCache()

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float] | None] = [None] * len(texts)
        missing: list[str] = []
        missing_indices: list[int] = []
        missing_keys: list[str] = []

        for idx, text in enumerate(texts):
            key = self._make_key(text)
            cached = await self.cache.get(key)
            if cached is not None:
                results[idx] = cached
            else:
                missing.append(text)
                missing_indices.append(idx)
                missing_keys.append(key)

        if missing:
            embeddings_client = get_embeddings()
            batch_size = settings.MAX_BATCH_EMBEDDINGS
            for start in range(0, len(missing), batch_size):
                batch = missing[start : start + batch_size]
                batch_indices = missing_indices[start : start + batch_size]
                batch_keys = missing_keys[start : start + batch_size]
                try:
                    vectors = await asyncio.wait_for(
                        embeddings_client.aembed_documents(batch),
                        timeout=settings.EMBEDDING_TIMEOUT_SECONDS,
                    )
                except asyncio.TimeoutError as exc:
                    logger.exception("Embedding batch timed out")
                    raise RuntimeError("Embedding request timed out") from exc
                for idx, key, vector in zip(batch_indices, batch_keys, vectors):
                    results[idx] = vector
                    await self.cache.set(key, vector)

        return [vector or [] for vector in results]

    async def embed_query(self, text: str) -> list[float]:
        embeddings_client = get_embeddings()
        try:
            return await asyncio.wait_for(
                embeddings_client.aembed_query(text),
                timeout=settings.EMBEDDING_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError as exc:
            logger.exception("Embedding query timed out")
            raise RuntimeError("Embedding request timed out") from exc

    def _make_key(self, text: str) -> str:
        hashed = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"emb:{settings.OPENAI_EMBEDDING_MODEL}:{hashed}"
