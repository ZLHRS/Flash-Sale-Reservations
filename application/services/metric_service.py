from domain.repositories.redis_repository import RedisRepository


class MetricsService:
    def __init__(self, redis: RedisRepository):
        self.redis = redis

    async def get_metrics(self):
        return await self.redis.get_metrics()
