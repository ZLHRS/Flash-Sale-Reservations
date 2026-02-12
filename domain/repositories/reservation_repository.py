from abc import ABC, abstractmethod
from typing import Optional, Union, List
from uuid import UUID
import datetime as dt

from domain.entities.reservation import Reservation
from presentation.schemas.reservation_scheme import ReservationStatus

ReservationId = Union[int, str, UUID]
ProductId = Union[int, str, UUID]
UserId = Union[int, str, UUID]


class ReservationRepository(ABC):
    @abstractmethod
    async def create(
        self,
        user_id: UserId,
        product_id: ProductId,
        expires_at: dt.datetime,
        status: ReservationStatus,
    ) -> Reservation: ...

    @abstractmethod
    async def get_by_id(
        self, reservation_id: ReservationId
    ) -> Optional[Reservation]: ...

    @abstractmethod
    async def get_for_update(
        self, reservation_id: ReservationId
    ) -> Optional[Reservation]: ...

    @abstractmethod
    async def has_active(self, user_id: UserId, product_id: ProductId) -> bool: ...

    @abstractmethod
    async def get_expired_active(
        self, now: dt.datetime, limit: int = 200
    ) -> List[Reservation]: ...

    @abstractmethod
    async def list(self, user_id=None, status=None, page: int = 1, size: int = 20): ...

    @abstractmethod
    async def count(self, user_id=None, status=None) -> int: ...
