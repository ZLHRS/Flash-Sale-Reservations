from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence, Optional, Union
from uuid import UUID

from domain.entities.product import Product

ProductId = Union[int, str, UUID]


class ProductRepository(ABC):
    @abstractmethod
    async def create(self, name: str, stock: int) -> Product: ...

    @abstractmethod
    async def get_by_id(self, product_id: ProductId) -> Optional[Product]: ...

    @abstractmethod
    async def get_for_update(self, product_id: ProductId) -> Optional[Product]: ...

    @abstractmethod
    async def list(self, page: int = 1, size: int = 20) -> Sequence[Product]: ...

    @abstractmethod
    async def count(self) -> int: ...
