from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.models.models import Base, User, Note, Todo, Reminder


# 构建数据库 URL
POSTGRES_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)


engine = create_async_engine(
    POSTGRES_DATABASE_URL,
    pool_size=20,  # 连接池大小
    max_overflow=10,  # 允许超出pool_size的连接数
    pool_timeout=30,  # 获取连接的超时时间(秒)
    pool_recycle=3600,  # 连接回收时间(秒)
    echo=True,  # 是否输出SQL日志，调试时可设为True
)


SessionLocal = async_sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=engine
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# Use Alembic, deprecated
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
