from app.evaluation.metrics import answer_coverage, hallucination_score
from app.evaluation.relevance import score_relevance


class EvaluationService:
    def compute(self, query_embedding, chunk_embeddings, answer: str, context: str) -> dict:
        valid_embeddings = [emb for emb in chunk_embeddings if emb is not None and len(emb) > 0]
        return {
            "context_relevance": score_relevance(query_embedding, valid_embeddings),
            "answer_coverage": answer_coverage(answer, context),
            "hallucination_score": hallucination_score(answer, context),
        }
