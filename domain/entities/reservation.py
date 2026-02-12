from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class Reservation:
    id: UUID | None = None
    user_id: UUID | None = None
    product_id: UUID | None = None

    status: str = "active"
    expires_at: datetime | None = None

    confirmed_at: datetime | None = None
    canceled_at: datetime | None = None

    created_at: datetime | None = None
