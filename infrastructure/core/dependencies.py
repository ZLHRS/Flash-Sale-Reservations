from __future__ import annotations
from typing import Annotated
from fastapi import Depends
from redis.asyncio import Redis

from infrastructure.redis.client import build_redis
from infrastructure.db.db_session import SessionDep
from domain.repositories.product_repository import ProductRepository
from domain.repositories.reservation_repository import ReservationRepository
from domain.repositories.outbox_repository import OutboxRepository
from domain.repositories.redis_repository import RedisRepository
from infrastructure.db.product_repository import SQLProductRepository
from infrastructure.db.reservation_repository import SQLReservationRepository
from infrastructure.db.outbox_repository import SQLOutboxRepository
from application.services.product_service import ProductService
from application.services.reservation_service import ReservationService
from application.services.metric_service import MetricsService
from infrastructure.redis.redis_repo import RealRedisRepository


async def get_product_repository(db: SessionDep) -> ProductRepository:
    return SQLProductRepository(db)


async def get_reservation_repository(db: SessionDep) -> ReservationRepository:
    return SQLReservationRepository(db)


async def get_outbox_repository(db: SessionDep) -> OutboxRepository:
    return SQLOutboxRepository(db)


def get_redis_repository(
    redis: Annotated[Redis, Depends(build_redis)],
) -> RedisRepository:
    return RealRedisRepository(redis)


ProductRepoDep = Annotated[ProductRepository, Depends(get_product_repository)]
ReservationRepoDep = Annotated[
    ReservationRepository, Depends(get_reservation_repository)
]
OutboxRepoDep = Annotated[OutboxRepository, Depends(get_outbox_repository)]
RedisRepoDep = Annotated[RedisRepository, Depends(get_redis_repository)]

# Services


def get_product_service(
    repo: ProductRepoDep,
) -> ProductService:
    return ProductService(product_repo=repo)


def get_reservation_service(
    db: SessionDep,
    product_repo: ProductRepoDep,
    reservation_repo: ReservationRepoDep,
    outbox_repo: OutboxRepoDep,
    redis: RedisRepoDep,
) -> ReservationService:
    return ReservationService(
        session=db,
        product_repo=product_repo,
        reservation_repo=reservation_repo,
        outbox_repo=outbox_repo,
        redis=redis,
    )


def get_metrics_service(redis: RedisRepoDep) -> MetricsService:
    return MetricsService(redis=redis)


ProductServiceDep = Annotated[ProductService, Depends(get_product_service)]
ReservationServiceDep = Annotated[ReservationService, Depends(get_reservation_service)]
MetricsServiceDep = Annotated[MetricsService, Depends(get_metrics_service)]
