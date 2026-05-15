from __future__ import annotations

import asyncio

from fastapi import HTTPException

from app.core.config import settings
from app.core.logging import get_logger
from app.retrieval.hybrid import lexical_score
from app.retrieval.rerank import rerank_chunks


logger = get_logger(__name__)


class RetrievalService:
    def __init__(self):
        from app.services.embedding_service import EmbeddingService

        self.embedding_service = EmbeddingService()
        self._vector_store = None

    async def _get_vector_store(self):
        if self._vector_store is None:
            from app.services.vector_store_service import VectorStoreService

            self._vector_store = await asyncio.to_thread(lambda: VectorStoreService().store)
        return self._vector_store

    async def retrieve(self, query: str, user_id: str, top_k: int, filters: dict | None = None):
        query_embedding = await asyncio.wait_for(
            self.embedding_service.embed_query(query),
            timeout=settings.EMBEDDING_TIMEOUT_SECONDS,
        )
        where = {"user_id": str(user_id)}
        if filters:
            where.update(filters)
        try:
            items = await asyncio.wait_for(
                asyncio.to_thread((await self._get_vector_store()).query, query_embedding, top_k, where),
                timeout=settings.VECTOR_STORE_TIMEOUT_SECONDS,
            )
        except Exception as exc:
            logger.exception("vector store query failed")
            raise HTTPException(status_code=503, detail="Vector store unavailable") from exc
        for item in items:
            lex = lexical_score(query, item.get("text", ""))
            item["score"] = (settings.HYBRID_ALPHA * item.get("score", 0.0)) + (
                (1.0 - settings.HYBRID_ALPHA) * lex
            )
        ranked = rerank_chunks(items, query)
        return ranked, query_embedding
