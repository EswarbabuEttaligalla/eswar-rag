from __future__ import annotations

from fastapi import HTTPException

from app.core.config import settings
from app.retrieval.hybrid import lexical_score
from app.retrieval.rerank import rerank_chunks


class RetrievalService:
    def __init__(self):
        from app.services.embedding_service import EmbeddingService

        self.embedding_service = EmbeddingService()
        self._vector_store = None

    def _get_vector_store(self):
        if self._vector_store is None:
            from app.services.vector_store_service import VectorStoreService

            self._vector_store = VectorStoreService().store
        return self._vector_store

    async def retrieve(self, query: str, user_id: str, top_k: int, filters: dict | None = None):
        query_embedding = await self.embedding_service.embed_query(query)
        where = {"user_id": str(user_id)}
        if filters:
            where.update(filters)
        try:
            items = self._get_vector_store().query(query_embedding, top_k=top_k, filters=where)
        except Exception as exc:
            raise HTTPException(status_code=503, detail="Vector store unavailable") from exc
        for item in items:
            lex = lexical_score(query, item.get("text", ""))
            item["score"] = (settings.HYBRID_ALPHA * item.get("score", 0.0)) + (
                (1.0 - settings.HYBRID_ALPHA) * lex
            )
        ranked = rerank_chunks(items, query)
        return ranked, query_embedding
