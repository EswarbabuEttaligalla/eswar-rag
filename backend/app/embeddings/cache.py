import json
from typing import Any

from redis.exceptions import RedisError

from app.caching.redis import get_redis
from app.core.config import settings


class EmbeddingCache:
    async def get(self, key: str) -> list[float] | None:
        try:
            redis_client = get_redis()
            value = await redis_client.get(key)
        except (RedisError, RuntimeError):
            return None
        if not value:
            return None
        return json.loads(value)

    async def set(self, key: str, vector: list[float]) -> None:
        try:
            redis_client = get_redis()
            await redis_client.set(key, json.dumps(vector), ex=settings.EMBEDDING_CACHE_TTL_SECONDS)
        except (RedisError, RuntimeError):
            return
