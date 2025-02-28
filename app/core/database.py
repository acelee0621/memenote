import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.models import Base, User, Note, Todo, Reminder

# 从环境变量获取数据库路径，默认为 data/memenote.sqlite3
database_path = os.getenv("SQLITE_DB_PATH", "data/memenote.sqlite3")
SQLITE_DATABASE_URL = f"sqlite+aiosqlite:///{database_path}"


engine = create_async_engine(
    SQLITE_DATABASE_URL, echo=True, execution_options={"sqlite_foreign_keys": True}
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
