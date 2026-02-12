from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.reservation_repository import ReservationRepository
from infrastructure.models.reservation_model import ReservationModel
from presentation.schemas.reservation_scheme import ReservationStatus


class SQLReservationRepository(ReservationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id, product_id, expires_at, status: ReservationStatus):
        reservation = ReservationModel(
            user_id=user_id,
            product_id=product_id,
            expires_at=expires_at,
            status=status.value if hasattr(status, "value") else status,
        )
        self.session.add(reservation)
        await self.session.flush()
        await self.session.refresh(reservation)
        return reservation

    async def get_by_id(self, reservation_id):
        result = await self.session.execute(
            select(ReservationModel).where(ReservationModel.id == reservation_id)
        )
        return result.scalar_one_or_none()

    async def get_for_update(self, reservation_id):
        result = await self.session.execute(
            select(ReservationModel)
            .where(ReservationModel.id == reservation_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def has_active(self, user_id, product_id) -> bool:
        result = await self.session.execute(
            select(ReservationModel.id)
            .where(
                and_(
                    ReservationModel.user_id == user_id,
                    ReservationModel.product_id == product_id,
                    ReservationModel.status == "active",
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def get_expired_active(self, now, limit: int = 200):
        result = await self.session.execute(
            select(ReservationModel)
            .where(
                and_(
                    ReservationModel.status == "active",
                    ReservationModel.expires_at <= now,
                )
            )
            .with_for_update(skip_locked=True)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list(self, user_id=None, status=None, page: int = 1, size: int = 20):
        stmt = select(ReservationModel)
        if user_id:
            stmt = stmt.where(ReservationModel.user_id == user_id)
        if status:
            stmt = stmt.where(ReservationModel.status == status.value)
        stmt = stmt.offset((page - 1) * size).limit(size)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, user_id=None, status=None) -> int:
        stmt = select(ReservationModel.id)
        if user_id:
            stmt = stmt.where(ReservationModel.user_id == user_id)
        if status:
            stmt = stmt.where(ReservationModel.status == status.value)

        result = await self.session.execute(stmt)
        return len(result.scalars().all())
