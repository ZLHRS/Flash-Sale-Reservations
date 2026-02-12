from __future__ import annotations
import datetime as dt
from uuid import UUID
from enum import Enum

from .base import BaseScheme


class OutboxEventType(str, Enum):
    RESERVATION_CONFIRMED = "reservation_confirmed"


class OutboxEventResponseScheme(BaseScheme):
    id: UUID

    event_type: OutboxEventType
    payload: str

    created_at: dt.datetime
