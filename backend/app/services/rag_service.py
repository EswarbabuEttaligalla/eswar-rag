from __future__ import annotations

import asyncio
import hashlib
import json
import re
from fastapi import HTTPException
from huggingface_hub import InferenceClient
from openai import AsyncOpenAI

from app.core.config import settings
from app.prompts.templates import build_prompt
from app.services.cache_service import CacheService
from app.services.evaluation_service import EvaluationService
from app.services.retrieval_service import RetrievalService
from app.utils.security import is_prompt_injection


class LLMClient:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_client = None
        self.hf_client = None
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise RuntimeError("OPENAI_API_KEY not configured")
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif self.provider == "huggingface":
            if not settings.HUGGINGFACEHUB_API_TOKEN:
                raise RuntimeError("HUGGINGFACEHUB_API_TOKEN not configured")
            self.hf_client = InferenceClient(
                model=settings.HUGGINGFACE_MODEL,
                token=settings.HUGGINGFACEHUB_API_TOKEN,
            )

    async def generate(self, prompt: str) -> str:
        if self.provider == "openai":
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
            )
            return response.choices[0].message.content or ""
        if self.provider == "huggingface":
            return await asyncio.to_thread(
                self.hf_client.text_generation,
                prompt,
                max_new_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                return_full_text=False,
            )
        raise RuntimeError("Unsupported LLM provider")

    async def stream(self, prompt: str):
        if self.provider == "openai":
            stream = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.MAX_TOKENS,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
            return
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

        chunks, query_embedding = await self.retrieval_service.retrieve(
            question, user_id=user_id, top_k=top_k, filters=filters
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
            answer = await self._llm().generate(prompt)
        except Exception:
            answer = self._build_fallback_answer(question, chunks)

        answer = self._normalize_answer(answer)

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
        chunks, _ = await self.retrieval_service.retrieve(question, user_id=user_id, top_k=top_k, filters=filters)
        if not chunks:
            yield "I do not have enough information to answer that question."
            return
        context = self._build_context(chunks)
        prompt = build_prompt(context, question, history)
        try:
            async for token in self._llm().stream(prompt):
                yield token
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
        direct_answer = self._extract_direct_answer(question, chunks)
        if direct_answer:
            return direct_answer
        selected_sentences: list[str] = []
        seen: set[str] = set()
        question_tokens = set(re.findall(r"[A-Za-z0-9]+", question.lower()))
        scored_sentences: list[tuple[float, str]] = []

        for item in chunks[:4]:
            base_score = float(item.get("score", 0.0))
            text = item.get("text", "")
            sentences = re.split(r"(?<=[.!?])\s+", text)
            for sentence in sentences:
                sentence = sentence.strip()
                normalized = re.sub(r"\s+", " ", sentence).strip()
                if len(normalized) < 20:
                    continue
                if normalized.lower() in seen:
                    continue
                sentence_tokens = set(re.findall(r"[A-Za-z0-9]+", normalized.lower()))
                overlap = len(question_tokens & sentence_tokens) / max(len(question_tokens), 1)
                scored_sentences.append(((base_score * 0.7) + (overlap * 0.3), normalized))
                seen.add(normalized.lower())

        scored_sentences.sort(key=lambda item: item[0], reverse=True)
        for _, sentence in scored_sentences[:2]:
            compact = self._compact_answer(sentence, question)
            if compact:
                selected_sentences.append(compact)

        if not selected_sentences:
            return "I do not have enough information to answer that question."
        if len(selected_sentences) == 1:
            return selected_sentences[0]
        return " ".join(selected_sentences[:2])

    def _extract_direct_answer(self, question: str, chunks: list[dict]) -> str | None:
        lowered = question.lower()
        priority_markers: list[tuple[set[str], list[str]]] = [
            ("skills" in lowered or "skill" in lowered, ["skills:", "skill:"]),
            (("school" in lowered) or ("study" in lowered) or ("studied" in lowered) or ("education" in lowered), ["education:", "studied at", "school:", "college:"]),
            (("build" in lowered) or ("built" in lowered) or ("project" in lowered) or ("experience" in lowered), ["experience:", "built", "worked on", "developed"]),
        ]
        normalized_chunks = [normalize_text(item.get("text", "")) for item in chunks]

        for condition, markers in priority_markers:
            if not condition:
                continue
            for chunk_text in normalized_chunks:
                chunk_lower = chunk_text.lower()
                if not any(marker in chunk_lower for marker in markers):
                    continue
                extracted = self._extract_marker_value(chunk_text, markers)
                if extracted:
                    return extracted

        return None

    def _extract_marker_value(self, text: str, markers: list[str]) -> str | None:
        lowered = text.lower()
        for marker in markers:
            if marker not in lowered:
                continue
            marker_index = lowered.index(marker)
            value = text[marker_index + len(marker) :].strip(" -:\n\t")
            if not value:
                continue
            value = value.split("\n")[0].strip()
            if marker.startswith("skills"):
                value = value.split(";", 1)[0].strip()
            if marker.startswith("education") or marker.startswith("school") or marker.startswith("college"):
                value = value.split("Skills:", 1)[0].strip()
            words = value.split()
            if len(words) > 16:
                value = " ".join(words[:16]).rstrip(".,;:")
            return value
        return None

    def _normalize_answer(self, answer: str) -> str:
        cleaned = re.sub(r"\s+", " ", answer).strip()
        cleaned = re.sub(r"(?i)\b(?:here is|here are|based on the context|the answer is)[:\s-]*", "", cleaned).strip()
        return cleaned

    def _compact_answer(self, sentence: str, question: str, max_words: int = 18) -> str:
        sentence = re.sub(r"\s+", " ", sentence).strip()
        for marker in ("Education:", "Skills:", "Experience:", "Projects:", "Summary:"):
            if marker in sentence:
                _, tail = sentence.split(marker, 1)
                sentence = tail.strip() or sentence
        words = sentence.split()
        if len(words) > max_words:
            sentence = " ".join(words[:max_words]).rstrip(".,;:")
        sentence = sentence.strip(" -:")
        return sentence


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace."""
    return re.sub(r"\s+", " ", text).strip()
