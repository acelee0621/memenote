import asyncio

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.models.models import Base
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.repository.user_repo import UserRepository
from app.schemas.schemas import UserCreate, UserResponse
from .helper import the_first_user


TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/memenote_test"
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    # poolclass=NullPool,
    # echo=True
)

TestingSessionLocal = async_sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=test_engine
)


# https://pypi.org/project/pytest-async-sqlalchemy/
# or poolclass = NullPool when create_async_engine
@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    """
    Creates an instance of the default event loop for the test session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


# 模拟一个用于测试认证的用户
@pytest_asyncio.fixture(scope="session")
async def test_user(override_get_db: AsyncSession):
    test_user = await UserRepository(override_get_db).create(UserCreate(**the_first_user))
    return UserResponse.model_validate(test_user)


# 测试客户端 fixture，包含依赖覆盖和清理
@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    # 设置依赖项覆盖
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as ac:
        yield ac
    # 清理依赖项覆盖
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def token(test_user: UserResponse) -> str:
    token = create_access_token({"sub": test_user.username})
    return token


@pytest_asyncio.fixture(scope="session")
async def authorized_client(
    client: AsyncClient, token: str, test_user: UserResponse
) -> AsyncGenerator[AsyncClient, None]:
    client.headers = {
        "Authorization": f"Bearer {token}",
        **client.headers,
    }
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield client
    app.dependency_overrides.clear()
