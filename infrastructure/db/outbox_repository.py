from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.outbox_repository import OutboxRepository
from infrastructure.models.outbox_event_model import OutboxEventModel


class SQLOutboxRepository(OutboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        event = OutboxEventModel(
            event_type=event_type,
            payload=payload,
        )
        self.session.add(event)
        await self.session.flush()
