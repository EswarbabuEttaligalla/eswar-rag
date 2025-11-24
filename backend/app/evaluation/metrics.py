from __future__ import annotations

import numpy as np
import re


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va = np.array(a)
    vb = np.array(b)
    if np.linalg.norm(va) == 0 or np.linalg.norm(vb) == 0:
        return 0.0
    return float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb)))


def answer_coverage(answer: str, context: str) -> float:
    tokens = set(re.findall(r"[A-Za-z0-9]+", answer.lower()))
    if not tokens:
        return 0.0
    context_tokens = set(re.findall(r"[A-Za-z0-9]+", context.lower()))
    return len(tokens & context_tokens) / len(tokens)


def hallucination_score(answer: str, context: str) -> float:
    coverage = answer_coverage(answer, context)
    return max(0.0, 1.0 - coverage)
