from pydantic import BaseModel


class SourceChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: dict


class RagMetrics(BaseModel):
    context_relevance: float
    answer_coverage: float
    hallucination_score: float


class QueryRequest(BaseModel):
    question: str
    top_k: int = 6
    filters: dict | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    metrics: RagMetrics
