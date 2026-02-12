from fastapi import APIRouter, status

from infrastructure.core.dependencies import ReservationServiceDep, MetricsServiceDep
from presentation.schemas.base import MetricsResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/sync-expired", status_code=status.HTTP_200_OK)
async def sync_expired(service: ReservationServiceDep):
    processed = await service.sync_expired()
    return {"expired_processed": processed}


@router.get("/metrics", response_model=MetricsResponse, status_code=status.HTTP_200_OK)
async def get_metrics(service: MetricsServiceDep):
    return await service.get_metrics()
