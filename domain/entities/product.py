from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class Product:
    id: UUID | None = None
    name: str = ""
    stock: int = 0
    created_at: datetime | None = None
