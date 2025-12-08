import json

from redis.exceptions import RedisError

from app.caching.redis import get_redis


class CacheService:
    async def get_json(self, key: str):
        try:
            redis_client = get_redis()
            value = await redis_client.get(key)
        except (RedisError, RuntimeError):
            return None
        return json.loads(value) if value else None

    async def set_json(self, key: str, value, ttl: int | None = None) -> None:
        try:
            redis_client = get_redis()
            payload = json.dumps(value)
            if ttl:
                await redis_client.set(key, payload, ex=ttl)
            else:
                await redis_client.set(key, payload)
        except (RedisError, RuntimeError):
            return

    async def delete(self, key: str) -> None:
        try:
            redis_client = get_redis()
            await redis_client.delete(key)
        except (RedisError, RuntimeError):
            return
