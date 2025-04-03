import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.models import Base, User, Note, Todo, Reminder

# 从环境变量获取 PostgreSQL 连接信息
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "memenote")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# 构建数据库 URL
POSTGRES_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


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
