import asyncio

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=settings.REQUEST_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning(
                "request timeout",
                method=request.method,
                path=str(request.url.path),
                request_id=getattr(request.state, "request_id", None),
                timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
            )
            return JSONResponse(
                status_code=504,
                content={"success": False, "error": "Request timed out"},
            )