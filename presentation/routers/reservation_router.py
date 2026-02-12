from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from presentation.schemas.reservation_scheme import (
    CreateReservationScheme,
    ReservationResponseScheme,
    ReservationListResponse,
    ReservationStatus,
)
from infrastructure.core.dependencies import ReservationServiceDep

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post(
    "",
    response_model=ReservationResponseScheme,
    status_code=status.HTTP_201_CREATED,
)
async def create_reservation(
    payload: CreateReservationScheme,
    service: ReservationServiceDep,
):
    return await service.create(payload)


@router.get("/{reservation_id}", response_model=ReservationResponseScheme)
async def get_reservation(
    reservation_id: UUID,
    service: ReservationServiceDep,
):
    reservation = await service.get_by_id(reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.post("/{reservation_id}/confirm", response_model=ReservationResponseScheme)
async def confirm_reservation(
    reservation_id: UUID,
    service: ReservationServiceDep,
):
    return await service.confirm(reservation_id)


@router.post("/{reservation_id}/cancel", response_model=ReservationResponseScheme)
async def cancel_reservation(
    reservation_id: UUID,
    service: ReservationServiceDep,
):
    return await service.cancel(reservation_id)


@router.get("", response_model=ReservationListResponse)
async def list_reservations(
    service: ReservationServiceDep,
    user_id: UUID | None = None,
    reservation_status: ReservationStatus | None = None,
    page: int = 1,
    size: int = 20,
):
    return await service.list(
        user_id=user_id, status=reservation_status, page=page, size=size
    )
