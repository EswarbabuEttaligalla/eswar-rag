from __future__ import annotations

import redis.asyncio as redis

from app.core.config import build_redis_url

redis_client: redis.Redis | None = None


async def init_redis() -> redis.Redis:
    global redis_client
    client = redis.from_url(build_redis_url(), decode_responses=True)
    await client.ping()
    redis_client = client
    return redis_client


def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
