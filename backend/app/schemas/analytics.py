from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_users: int
    total_documents: int
    total_queries: int
    avg_latency_ms: float
