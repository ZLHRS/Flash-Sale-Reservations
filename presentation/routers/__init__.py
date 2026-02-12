from fastapi import APIRouter
from .admin_router import router as admin_router
from .product_router import router as product_router
from .reservation_router import router as reservation_router

main_router = APIRouter(prefix="/api/v1")

routers = [
    admin_router,
    product_router,
    reservation_router,
]
for router in routers:
    main_router.include_router(router)
