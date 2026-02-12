from __future__ import annotations
import datetime as dt
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from enum import Enum

from .base import BaseScheme


class ReservationStatus(str, Enum):
    ACTIVE = "active"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"
    EXPIRED = "expired"


class CreateReservationScheme(BaseModel):
    product_id: UUID
    user_id: UUID


class ReservationResponseScheme(BaseScheme):
    id: UUID
    product_id: UUID
    user_id: UUID

    status: ReservationStatus

    expires_at: dt.datetime

    confirmed_at: Optional[dt.datetime] = None
    canceled_at: Optional[dt.datetime] = None

    created_at: dt.datetime
    updated_at: dt.datetime


class ConfirmReservationScheme(BaseModel):
    reservation_id: UUID


class CancelReservationScheme(BaseModel):
    reservation_id: UUID


class ReservationFilterParams(BaseModel):
    user_id: Optional[UUID] = None
    status: Optional[ReservationStatus] = None


class Pagination(BaseModel):
    total: int
    page: int
    size: int
    total_pages: int


class ReservationListResponse(BaseModel):
    items: List[ReservationResponseScheme]
    pagination: Pagination
