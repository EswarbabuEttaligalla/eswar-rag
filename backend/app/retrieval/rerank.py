from __future__ import annotations

from typing import Iterable


def rerank_chunks(chunks: list[dict], query: str) -> list[dict]:
    return sorted(chunks, key=lambda item: item.get("score", 0.0), reverse=True)
