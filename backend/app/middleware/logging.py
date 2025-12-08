import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        latency_ms = (time.monotonic() - start) * 1000
        logger.info(
            "request",
            method=request.method,
            path=str(request.url.path),
            status=response.status_code,
            latency_ms=round(latency_ms, 2),
            request_id=getattr(request.state, "request_id", None),
        )
        return response
