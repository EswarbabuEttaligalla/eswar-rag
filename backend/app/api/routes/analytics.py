from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.schemas.analytics import AnalyticsOverview
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview)
async def overview(session: AsyncSession = Depends(get_db), admin=Depends(get_current_admin)):
    service = AnalyticsService(session)
    data = await service.overview()
    return AnalyticsOverview(**data)
