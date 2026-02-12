from __future__ import annotations
import datetime as dt
from typing import List
from pydantic import BaseModel, Field
from uuid import UUID

from .base import BaseScheme


class CreateProductScheme(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    stock: int = Field(ge=0)


class ProductResponseScheme(BaseScheme):
    id: UUID
    name: str
    stock: int

    created_at: dt.datetime
    updated_at: dt.datetime


class ProductListResponse(BaseModel):
    items: List[ProductResponseScheme]
    total: int
    page: int
    size: int
