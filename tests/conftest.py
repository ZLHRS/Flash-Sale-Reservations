import os
import pytest
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from redis.asyncio import Redis

API_URL = "http://test"


os.environ.setdefault(
    "POSTGRES_URL",
    "postgresql+asyncpg://flashsale:flashsale@db_test:5432/flashsale_test",
)
os.environ.setdefault("POSTGRES_HOST", "db_test")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "flashsale_test")

os.environ.setdefault("REDIS_HOST", "redis")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_URL", "redis://redis:6379/0")


@pytest.fixture
def db_url():
    return "postgresql+asyncpg://flashsale:flashsale@db_test:5432/flashsale_test"


@pytest.fixture
async def engine(db_url):
    eng = create_async_engine(db_url, poolclass=NullPool, pool_pre_ping=True)
    try:
        yield eng
    finally:
        await eng.dispose()


@pytest.fixture
def sessionmaker(engine):
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def clean_db(engine):
    async with engine.begin() as conn:
        # добавь сюда ВСЕ таблицы, которые трогают тесты
        await conn.exec_driver_sql(
            "TRUNCATE TABLE outbox_events RESTART IDENTITY CASCADE;"
        )
        await conn.exec_driver_sql(
            "TRUNCATE TABLE reservations RESTART IDENTITY CASCADE;"
        )
        await conn.exec_driver_sql("TRUNCATE TABLE products RESTART IDENTITY CASCADE;")


@pytest.fixture
async def app(sessionmaker):
    from main import app
    from infrastructure.db.db_session import get_session
    from infrastructure.redis.client import build_redis

    async def override_get_session():
        async with sessionmaker() as s:
            yield s

    from redis.asyncio import Redis

    async def override_build_redis():
        redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
        try:
            yield redis
        finally:
            await redis.aclose()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[build_redis] = override_build_redis

    yield app

    app.dependency_overrides.clear()


@pytest.fixture
async def client(app, clean_db):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url=API_URL) as c:
        yield c
