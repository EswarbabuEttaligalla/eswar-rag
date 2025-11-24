from app.evaluation.metrics import hallucination_score


def score_hallucination(answer: str, context: str) -> float:
    return hallucination_score(answer, context)
