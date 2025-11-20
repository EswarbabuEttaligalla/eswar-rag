from __future__ import annotations

import re

from app.utils.text_utils import normalize_text


def _token_overlap_score(query: str, text: str) -> float:
    query_tokens = {token for token in re.findall(r"[A-Za-z0-9]+", query.lower()) if len(token) > 1}
    text_tokens = {token for token in re.findall(r"[A-Za-z0-9]+", text.lower()) if len(token) > 1}
    if not query_tokens or not text_tokens:
        return 0.0
    return len(query_tokens & text_tokens) / len(query_tokens)


def rerank_chunks(chunks: list[dict], query: str) -> list[dict]:
    ranked = []
    for item in chunks:
        text = item.get("text", "")
        overlap = _token_overlap_score(query, text)
        score = item.get("score", 0.0)
        item["score"] = (0.8 * score) + (0.2 * overlap)
        ranked.append(item)
    return sorted(
        ranked,
        key=lambda item: (item.get("score", 0.0), len(normalize_text(item.get("text", "")))),
        reverse=True,
    )
