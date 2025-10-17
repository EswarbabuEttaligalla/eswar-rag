from sqlalchemy import Float, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analytics import AnalyticsEvent


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event: AnalyticsEvent):
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def count_by_type(self, event_type: str) -> int:
        result = await self.session.execute(
            select(func.count(AnalyticsEvent.id)).where(AnalyticsEvent.event_type == event_type)
        )
        return int(result.scalar() or 0)

    async def avg_latency(self) -> float:
        result = await self.session.execute(
            select(func.avg(cast(AnalyticsEvent.payload["latency_ms"].astext, Float)))
            .where(AnalyticsEvent.event_type == "query")
        )
        return float(result.scalar() or 0.0)
