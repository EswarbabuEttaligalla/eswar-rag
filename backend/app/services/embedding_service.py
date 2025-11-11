from __future__ import annotations

import asyncio
import hashlib

from app.embeddings.cache import EmbeddingCache
from app.embeddings.hf import get_model
from app.core.config import settings


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
            model = get_model()
            batch_size = settings.MAX_BATCH_EMBEDDINGS
            for start in range(0, len(missing), batch_size):
                batch = missing[start : start + batch_size]
                batch_indices = missing_indices[start : start + batch_size]
                batch_keys = missing_keys[start : start + batch_size]
                embeddings = await asyncio.to_thread(
                    model.encode,
                    batch,
                    normalize_embeddings=True,
                    convert_to_numpy=False,
                )
                for idx, key, emb in zip(batch_indices, batch_keys, embeddings):
                    vector = emb.tolist() if hasattr(emb, "tolist") else list(emb)
                    results[idx] = vector
                    await self.cache.set(key, vector)

        return [vector or [] for vector in results]

    async def embed_query(self, text: str) -> list[float]:
        return (await self.embed_texts([text]))[0]

    def _make_key(self, text: str) -> str:
        hashed = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"emb:{settings.EMBEDDING_MODEL}:{hashed}"
