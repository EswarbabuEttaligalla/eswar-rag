from __future__ import annotations

import re

from fastapi import HTTPException

from app.core.config import settings
from app.utils.text_utils import normalize_text
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

        filtered_items: list[dict] = []
        seen_texts: set[str] = set()
        for item in items:
            lex = lexical_score(query, item.get("text", ""))
            score = (settings.HYBRID_ALPHA * item.get("score", 0.0)) + (
                (1.0 - settings.HYBRID_ALPHA) * lex
            )
            if score < 0.18:
                continue
            text_key = normalize_text(item.get("text", "")).lower()
            if not text_key or text_key in seen_texts:
                continue
            seen_texts.add(text_key)
            item["score"] = score
            filtered_items.append(item)

        ranked = rerank_chunks(filtered_items, query)
        return ranked[: max(1, min(top_k, settings.MAX_CONTEXT_CHUNKS, 4))], query_embedding
