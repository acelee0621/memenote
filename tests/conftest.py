import pytest_asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.main import app
from app.models.models import Base
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import UserResponse

# 创建测试客户端
client = TestClient(app)


# 使用内存中的 SQLite 数据库进行测试
TEST_SQLITE_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 创建测试用的异步引擎
test_engine = create_async_engine(
    TEST_SQLITE_DATABASE_URL,
    echo=True,
    execution_options={"sqlite_foreign_keys": True},
)

# 创建测试用的异步会话工厂
TestingSessionLocal = async_sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=test_engine
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        # 删除所有表
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    return _override_get_db


# 模拟一个认证用户
@pytest_asyncio.fixture
def mock_user():
    return UserResponse(
        id="777",
        username="testuser",
        full_name="Test User",
        email="test@example.com",
        created_at="2023-10-01T00:00:00Z",
        updated_at="2023-10-01T00:00:00Z",
    )
