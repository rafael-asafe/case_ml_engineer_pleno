import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

import microservice_nre.lifespan as lifespan_module
from microservice_nre.database.database import get_session
from microservice_nre.database.models import table_registry
from microservice_nre.main import app

DATABASE_URL = 'sqlite+aiosqlite:///:memory:'


@pytest_asyncio.fixture
async def engine():
    _engine = create_async_engine(
        DATABASE_URL,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with _engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    yield _engine

    async with _engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def session(engine):
    async with AsyncSession(engine, expire_on_commit=False) as s:
        yield s


@pytest.fixture
def client(engine, session):
    async def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override

    original_engine = lifespan_module.engine
    lifespan_module.engine = engine

    with TestClient(app) as test_client:
        yield test_client

    lifespan_module.engine = original_engine
    app.dependency_overrides.clear()
