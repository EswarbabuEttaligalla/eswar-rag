from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI

from app.core.config import settings
from app.db.init_db import init_db
from app.caching.redis import init_redis, close_redis
from app.logging.setup import configure_logging
from app.utils.file_utils import ensure_dirs


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    ensure_dirs([settings.DATA_DIR, settings.UPLOAD_DIR, settings.VECTOR_DIR])
    try:
        await init_db()
    except Exception:
        logger.exception("Database initialization failed")
        raise
    try:
        await init_redis()
    except Exception as exc:
        logger.warning("Redis initialization skipped: %s", exc)
    yield
    try:
        await close_redis()
    except Exception as exc:
        logger.warning("Redis cleanup failed: %s", exc)
