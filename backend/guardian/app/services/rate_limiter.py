import time

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()
_redis_client = None


async def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = await redis.from_url(
            settings.redis_url, decode_responses=True
        )
    return _redis_client


async def check_rate_limit(
    tenant_id: str, api_key_hash: str, limit: int, window_seconds: int
) -> bool:
    """
    Check if request is within rate limit using sliding window algorithm.
    Returns True if allowed, False if limit exceeded.
    """
    if not settings.rate_limit_enabled:
        return True

    try:
        client = await get_redis_client()
        key = f"rate_limit:{tenant_id}:{api_key_hash}"
        now = time.time()
        window_start = now - window_seconds

        await client.zremrangebyscore(key, "-inf", window_start)
        count = await client.zcard(key)

        if count >= limit:
            return False

        await client.zadd(key, {str(now): now})
        await client.expire(key, window_seconds)

        return True
    except Exception:
        return True

