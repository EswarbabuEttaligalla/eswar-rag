from __future__ import annotations

import asyncio
import hashlib
import logging
import json
from fastapi import HTTPException
from openai import AsyncOpenAI

from app.core.config import settings
from app.prompts.templates import build_prompt
from app.services.cache_service import CacheService
from app.services.evaluation_service import EvaluationService
from app.services.retrieval_service import RetrievalService
from app.utils.security import is_prompt_injection


logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS,
                max_retries=settings.OPENAI_MAX_RETRIES,
            )

    async def generate(self, prompt: str) -> str:
        if self.openai_client is None:
            raise RuntimeError("OPENAI_API_KEY not configured")
        response = await asyncio.wait_for(
            self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
            ),
            timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS,
        )
        return response.choices[0].message.content or ""

    async def stream(self, prompt: str):
        text = await self.generate(prompt)
        for i in range(0, len(text), 20):
            yield text[i : i + 20]


class RagService:
    def __init__(self):
        self.retrieval_service = RetrievalService()
        self.evaluation_service = EvaluationService()
        self.cache = CacheService()
        self._llm_client = None

    def _llm(self) -> LLMClient:
        if self._llm_client is None:
            self._llm_client = LLMClient()
        return self._llm_client

    async def answer(
        self,
        question: str,
        user_id: str,
        top_k: int = 6,
        filters: dict | None = None,
        history: str | None = None,
    ):
        if is_prompt_injection(question):
            raise HTTPException(status_code=400, detail="Potential prompt injection detected")

        cache_seed = json.dumps({"q": question, "h": history, "f": filters, "k": top_k}, sort_keys=True)
        cache_key = f"rag:{user_id}:{hashlib.sha256(cache_seed.encode('utf-8')).hexdigest()}"
        cached = await self.cache.get_json(cache_key)
        if cached:
            return cached

        chunks, query_embedding = await asyncio.wait_for(
            self.retrieval_service.retrieve(question, user_id=user_id, top_k=top_k, filters=filters),
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
        if not chunks:
            empty_response = {
                "answer": "I do not have enough information to answer that question.",
                "sources": [],
                "metrics": {"context_relevance": 0.0, "answer_coverage": 0.0, "hallucination_score": 1.0},
            }
            await self.cache.set_json(cache_key, empty_response, ttl=300)
            return empty_response
        context = self._build_context(chunks)
        prompt = build_prompt(context, question, history)
        try:
            answer = await asyncio.wait_for(self._llm().generate(prompt), timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS)
        except Exception as exc:
            logger.warning("LLM generation failed, using fallback answer: %s", exc)
            answer = self._build_fallback_answer(question, chunks)

        chunk_embeddings = [item.get("embedding", []) for item in chunks]
        metrics = self.evaluation_service.compute(query_embedding, chunk_embeddings, answer, context)
        response = {"answer": answer, "sources": self._build_sources(chunks), "metrics": metrics}
        await self.cache.set_json(cache_key, response, ttl=300)
        return response

    async def stream_answer(
        self,
        question: str,
        user_id: str,
        top_k: int = 6,
        filters: dict | None = None,
        history: str | None = None,
    ):
        if is_prompt_injection(question):
            raise HTTPException(status_code=400, detail="Potential prompt injection detected")
        chunks, _ = await asyncio.wait_for(
            self.retrieval_service.retrieve(question, user_id=user_id, top_k=top_k, filters=filters),
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
        if not chunks:
            yield "I do not have enough information to answer that question."
            return
        context = self._build_context(chunks)
        prompt = build_prompt(context, question, history)
        try:
            answer = await asyncio.wait_for(self._llm().generate(prompt), timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS)
            for i in range(0, len(answer), 20):
                yield answer[i : i + 20]
        except Exception:
            yield self._build_fallback_answer(question, chunks)

    def _build_context(self, chunks: list[dict]) -> str:
        lines = []
        for idx, item in enumerate(chunks, start=1):
            doc_id = item.get("metadata", {}).get("document_id")
            chunk_id = item.get("id")
            lines.append(f"[{idx}] ({doc_id}:{chunk_id}) {item.get('text', '')}")
        return "\n\n".join(lines)

    def _build_sources(self, chunks: list[dict]) -> list[dict]:
        sources = []
        for item in chunks:
            sources.append(
                {
                    "chunk_id": item.get("id"),
                    "document_id": item.get("metadata", {}).get("document_id"),
                    "text": item.get("text", "")[:500],
                    "score": item.get("score", 0.0),
                    "metadata": item.get("metadata", {}),
                }
            )
        return sources

    def _build_fallback_answer(self, question: str, chunks: list[dict]) -> str:
        if not chunks:
            return "I do not have enough information to answer that question."
        snippets = []
        for item in chunks[:3]:
            text = item.get("text", "").strip()
            if text:
                snippets.append(text[:300])
        if not snippets:
            return "I found related documents, but could not extract readable context from them."
        joined = "\n\n".join(snippets)
        return f"I found relevant context for '{question}':\n\n{joined}"
