from typing import Optional
from uuid import UUID
from redis.asyncio import Redis

from domain.repositories.redis_repository import RedisRepository


class RealRedisRepository(RedisRepository):
    def __init__(self, redis: Redis):
        self.redis = redis

    def _ttl_key(self, reservation_id: UUID) -> str:
        return f"reservation:{reservation_id}"

    def _metric_key(self, name: str) -> str:
        return f"metrics:{name}"

    async def set_reservation_ttl(self, reservation_id: UUID, ttl_seconds: int) -> None:
        await self.redis.set(self._ttl_key(reservation_id), "1", ex=ttl_seconds)

    async def delete_reservation_ttl(self, reservation_id: UUID) -> None:
        await self.redis.delete(self._ttl_key(reservation_id))

    async def get_reservation_ttl(self, reservation_id: UUID) -> Optional[int]:
        t = await self.redis.ttl(self._ttl_key(reservation_id))
        if t is None or t < 0:
            return None
        return int(t)

    async def incr_metric(self, name: str, amount: int = 1) -> int:
        return int(await self.redis.incrby(self._metric_key(name), amount))

    async def get_metrics(self) -> dict[str, int]:
        keys = [
            "reservations_created",
            "reservations_confirmed",
            "reservations_canceled",
            "reservations_expired",
        ]
        redis_keys = [self._metric_key(k) for k in keys]
        values = await self.redis.mget(redis_keys)

        out: dict[str, int] = {}
        for k, v in zip(keys, values, strict=False):
            out[k] = int(v) if v is not None else 0
        return out
