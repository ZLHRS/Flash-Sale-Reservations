from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class RedisRepository(ABC):
    @abstractmethod
    async def set_reservation_ttl(
        self, reservation_id: UUID, ttl_seconds: int
    ) -> None: ...

    @abstractmethod
    async def delete_reservation_ttl(self, reservation_id: UUID) -> None: ...

    @abstractmethod
    async def get_reservation_ttl(self, reservation_id: UUID) -> Optional[int]: ...

    @abstractmethod
    async def incr_metric(self, name: str, amount: int = 1) -> int: ...

    @abstractmethod
    async def get_metrics(self) -> dict[str, int]: ...
