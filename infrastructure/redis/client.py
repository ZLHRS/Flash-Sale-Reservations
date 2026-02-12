from __future__ import annotations

from typing import AsyncIterator
from redis.asyncio import Redis
from infrastructure.core.config import settings


async def build_redis() -> AsyncIterator[Redis]:
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.aclose()
