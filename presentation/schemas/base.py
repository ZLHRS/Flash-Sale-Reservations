from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MetricsResponse(BaseModel):
    reservations_created: int
    reservations_confirmed: int
    reservations_canceled: int
    reservations_expired: int


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[str] = None
