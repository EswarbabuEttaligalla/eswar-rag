import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.retrieval import QueryRequest, QueryResponse
from app.services.analytics_service import AnalyticsService
from app.services.rag_service import RagService

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    session: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    service = RagService()
    start = time.monotonic()
    response = await service.answer(payload.question, user_id=str(user.id), top_k=payload.top_k, filters=payload.filters)
    latency_ms = (time.monotonic() - start) * 1000
    token_count = len(response.get("answer", "").split())
    await AnalyticsService(session).record_event(
        "query",
        user_id=user.id,
        payload={
            "latency_ms": round(latency_ms, 2),
            "model": "rag",
            "token_count": token_count,
        },
    )
    return response
