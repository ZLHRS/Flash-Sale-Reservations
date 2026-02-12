from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import Annotated

from infrastructure.core.config import settings

engine = create_async_engine(
    settings.database_url_asyncpg,
    connect_args={"server_settings": {"search_path": "public"}},
    pool_pre_ping=True,
)
session_local = async_sessionmaker(
    expire_on_commit=False, class_=AsyncSession, bind=engine
)


async def get_session():
    async with session_local() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
