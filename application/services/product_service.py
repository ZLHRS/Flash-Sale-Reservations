class ProductService:
    def __init__(self, product_repo):
        self.product_repo = product_repo

    async def create(self, payload):
        return await self.product_repo.create(
            name=payload.name,
            stock=payload.stock,
        )

    async def get_by_id(self, product_id):
        return await self.product_repo.get_by_id(product_id)

    async def list(self, page: int, size: int):
        items = await self.product_repo.list(page=page, size=size)
        total = await self.product_repo.count()
        return {"items": items, "total": total, "page": page, "size": size}
