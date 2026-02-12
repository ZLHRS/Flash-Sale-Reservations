from fastapi import APIRouter, status, HTTPException
from uuid import UUID

from presentation.schemas.product_scheme import (
    CreateProductScheme,
    ProductResponseScheme,
    ProductListResponse,
)
from infrastructure.core.dependencies import ProductServiceDep

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponseScheme,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    payload: CreateProductScheme,
    service: ProductServiceDep,
):
    return await service.create(payload)


@router.get("", response_model=ProductListResponse)
async def list_products(
    service: ProductServiceDep,
    page: int = 1,
    size: int = 20,
):
    return await service.list(page=page, size=size)


@router.get("/{product_id}", response_model=ProductResponseScheme)
async def get_product(
    product_id: UUID,
    service: ProductServiceDep,
):
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product
