from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Union
from uuid import UUID

from typing import Dict, Any

OutboxEventId = Union[int, str, UUID]


class OutboxRepository(ABC):
    @abstractmethod
    async def create_event(self, event_type: str, payload: Dict[str, Any]) -> None: ...
