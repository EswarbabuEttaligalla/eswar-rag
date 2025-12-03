from sqlalchemy import func, select

from app.core.config import settings
from app.models.analytics import AnalyticsEvent
from app.models.document import Document
from app.models.user import User
from app.repositories.analytics_repo import AnalyticsRepository


class AnalyticsService:
    def __init__(self, session):
        self.session = session
        self.repo = AnalyticsRepository(session)

    async def record_event(self, event_type: str, user_id=None, payload: dict | None = None):
        if not settings.ENABLE_ANALYTICS:
            return None
        event = AnalyticsEvent(user_id=user_id, event_type=event_type, payload=payload or {})
        return await self.repo.create(event)

    async def overview(self) -> dict:
        total_users = await self._count_users()
        total_documents = await self._count_documents()
        total_queries = await self.repo.count_by_type("query")
        avg_latency_ms = await self.repo.avg_latency()
        return {
            "total_users": total_users,
            "total_documents": total_documents,
            "total_queries": total_queries,
            "avg_latency_ms": avg_latency_ms,
        }

    async def _count_users(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return int(result.scalar() or 0)

    async def _count_documents(self) -> int:
        result = await self.session.execute(select(func.count(Document.id)))
        return int(result.scalar() or 0)
