import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.embeddings.openai_embeddings import get_embeddings
from app.services.vector_store_service import VectorStoreService

router = APIRouter()


@router.get("/health")
async def health_check():
    checks = {"database": "unknown", "vector_store": "unknown", "openai": "unknown"}
    status_code = 200

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"
        status_code = 503

    try:
        await asyncio.wait_for(asyncio.to_thread(lambda: VectorStoreService().store), timeout=settings.VECTOR_STORE_TIMEOUT_SECONDS)
        checks["vector_store"] = "ok"
    except Exception as exc:
        checks["vector_store"] = f"error: {exc}"
        status_code = 503

    try:
        embeddings = get_embeddings()
        await asyncio.wait_for(embeddings.aembed_query("health check"), timeout=settings.EMBEDDING_TIMEOUT_SECONDS)
        checks["openai"] = "ok"
    except Exception as exc:
        checks["openai"] = f"error: {exc}"
        status_code = 503

    payload = {"status": "ok" if status_code == 200 else "degraded", "checks": checks}
    return JSONResponse(status_code=status_code, content=payload)
