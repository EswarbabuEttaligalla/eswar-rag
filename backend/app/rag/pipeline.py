from __future__ import annotations

from app.services.retrieval_service import RetrievalService
from app.services.rag_service import RagService


class RagPipeline:
    def __init__(self, retrieval_service: RetrievalService, rag_service: RagService):
        self.retrieval_service = retrieval_service
        self.rag_service = rag_service
