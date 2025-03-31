import asyncio

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.models.models import Base
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import UserResponse


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/memenote_test"
)


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    # echo=True
)


TestingSessionLocal = async_sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=test_engine
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


# https://pypi.org/project/pytest-async-sqlalchemy/
# or poolclass = NullPool when create_async_engine
# @pytest_asyncio.fixture(scope="session", autouse=True)
# def event_loop():
#     """
#     Creates an instance of the default event loop for the test session.
#     """
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session
    return _override_get_db


# 模拟一个用于测试认证的用户
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    from app.core.security import get_password_hash
    from .helper import the_first_user

    the_first_user["password_hash"] = get_password_hash(the_first_user.pop("password"))

    user = User(**the_first_user)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return UserResponse.model_validate(user)
    # return user


# 测试客户端 fixture，包含依赖覆盖和清理
@pytest_asyncio.fixture
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    # 设置依赖项覆盖
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    # 清理依赖项覆盖
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(
    client: AsyncClient, test_user: UserResponse
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


# 不带认证的默认 client
@pytest_asyncio.fixture
async def non_auth_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
