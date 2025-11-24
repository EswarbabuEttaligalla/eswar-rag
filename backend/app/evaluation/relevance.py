from app.evaluation.metrics import cosine_similarity


def score_relevance(query_embedding: list[float], chunk_embeddings: list[list[float]]) -> float:
    if not chunk_embeddings:
        return 0.0
    scores = [cosine_similarity(query_embedding, emb) for emb in chunk_embeddings]
    return sum(scores) / len(scores)
