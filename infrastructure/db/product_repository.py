from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories.product_repository import ProductRepository
from infrastructure.models.product_model import ProductModel


class SQLProductRepository(ProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, stock: int):
        product = ProductModel(name=name, stock=stock)
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def get_by_id(self, product_id):
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id)
        )
        return result.scalar_one_or_none()

    async def list(self, page: int = 1, size: int = 20):
        result = await self.session.execute(
            select(ProductModel).offset((page - 1) * size).limit(size)
        )
        return list(result.scalars())

    async def count(self) -> int:
        result = await self.session.execute(select(ProductModel.id))
        return len(result.scalars().all())

    async def get_for_update(self, product_id):
        result = await self.session.execute(
            select(ProductModel).where(ProductModel.id == product_id).with_for_update()
        )
        return result.scalar_one_or_none()
