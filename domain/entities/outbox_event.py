from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class OutboxEvent:
    id: UUID | None = None
    event_type: str = ""
    payload: dict | None = None
    occurred_at: datetime | None = None
