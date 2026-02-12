from datetime import datetime, UTC, timedelta
from uuid import UUID
import math
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.outbox_repository import OutboxRepository
from domain.repositories.product_repository import ProductRepository
from domain.repositories.reservation_repository import ReservationRepository
from infrastructure.core.config import settings
from presentation.schemas.reservation_scheme import ReservationStatus
from domain.repositories.redis_repository import RedisRepository


class ReservationService:
    def __init__(
        self,
        session: AsyncSession,
        product_repo: ProductRepository,
        reservation_repo: ReservationRepository,
        outbox_repo: OutboxRepository,
        redis: RedisRepository,
    ):
        self.session = session
        self.product_repo = product_repo
        self.reservation_repo = reservation_repo
        self.outbox_repo = outbox_repo
        self.redis = redis

    async def get_by_id(self, reservation_id: UUID):
        return await self.reservation_repo.get_by_id(reservation_id)

    async def create(self, payload):
        expires_at = datetime.now(UTC) + timedelta(
            seconds=settings.RESERVATION_TTL_SECONDS
        )
        try:
            async with self.session.begin():
                product = await self.product_repo.get_for_update(payload.product_id)
                if not product:
                    raise HTTPException(404, "Product not found")
                if product.stock <= 0:
                    raise HTTPException(409, "Product out of stock")
                if await self.reservation_repo.has_active(
                    payload.user_id, payload.product_id
                ):
                    raise HTTPException(409, "Active reservation already exists")
                product.stock -= 1
                reservation = await self.reservation_repo.create(
                    user_id=payload.user_id,
                    product_id=payload.product_id,
                    expires_at=expires_at,
                    status=ReservationStatus.ACTIVE,
                )
        except IntegrityError:
            raise HTTPException(409, "Active reservation already exists")
        await self.redis.set_reservation_ttl(
            reservation.id, settings.RESERVATION_TTL_SECONDS
        )
        await self.redis.incr_metric("reservations_created", 1)
        return reservation

    async def confirm(self, reservation_id: UUID):
        async with self.session.begin():
            reservation = await self.reservation_repo.get_for_update(reservation_id)
            if not reservation:
                raise HTTPException(404, "Reservation not found")
            if reservation.status != ReservationStatus.ACTIVE:
                raise HTTPException(409, "Reservation not active")
            if reservation.expires_at is None:
                raise HTTPException(500, "Reservation corrupted: expires_at is null")
            if reservation.expires_at <= datetime.now(UTC):
                raise HTTPException(409, "Reservation expired")
            reservation.status = ReservationStatus.CONFIRMED
            reservation.confirmed_at = datetime.now(UTC)
            await self.outbox_repo.create_event(
                event_type="reservation_confirmed",
                payload={
                    "reservation_id": str(reservation.id),
                    "user_id": str(reservation.user_id),
                    "product_id": str(reservation.product_id),
                },
            )
        await self.redis.delete_reservation_ttl(reservation_id)
        await self.redis.incr_metric("reservations_confirmed", 1)
        return reservation

    async def cancel(self, reservation_id: UUID):
        async with self.session.begin():
            reservation = await self.reservation_repo.get_for_update(reservation_id)
            if not reservation:
                raise HTTPException(404, "Reservation not found")
            if reservation.status != ReservationStatus.ACTIVE:
                raise HTTPException(409, "Reservation not active")
            pid = reservation.product_id
            if pid is None:
                raise HTTPException(500, "Reservation corrupted: product_id is null")
            product = await self.product_repo.get_for_update(pid)
            if product is None:
                raise HTTPException(404, "Product not found")
            reservation.status = ReservationStatus.CANCELED
            reservation.canceled_at = datetime.now(UTC)
            product.stock += 1
        await self.redis.delete_reservation_ttl(reservation_id)
        await self.redis.incr_metric("reservations_canceled", 1)
        return reservation

    async def sync_expired(self) -> int:
        now = datetime.now(UTC)
        tx = self.session.get_transaction()
        ctx = self.session.begin_nested() if tx is not None else self.session.begin()
        async with ctx:
            expired = await self.reservation_repo.get_expired_active(now)
            for r in expired:
                if r.status != ReservationStatus.ACTIVE:
                    continue
                pid = r.product_id
                assert pid is not None
                product = await self.product_repo.get_for_update(pid)
                if product is None:
                    raise HTTPException(404, "Product not found")
                r.status = ReservationStatus.EXPIRED
                product.stock += 1
            await self.session.flush()
        if expired:
            await self.redis.incr_metric("reservations_expired", len(expired))
        return len(expired)

    async def list(
        self,
        user_id: UUID | None,
        status: ReservationStatus | None,
        page: int,
        size: int,
    ):
        items = await self.reservation_repo.list(
            user_id=user_id, status=status, page=page, size=size
        )
        total = await self.reservation_repo.count(user_id=user_id, status=status)
        total_pages = math.ceil(total / size) if size else 1
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages,
            },
        }
