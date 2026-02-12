from datetime import datetime, UTC
from sqlalchemy import String, Integer, CheckConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.models.base import HasId


class ProductModel(HasId):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_product_stock_non_negative"),
    )
