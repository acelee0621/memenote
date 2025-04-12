import os
from fastapi import FastAPI, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.redis_db import redis_connect
from app.core.s3_client import ensure_minio_bucket_exists
from app.core.user_manage import auth_backend, get_current_user, fastapi_users
from app.models.models import User
from app.schemas.schemas import UserRead, UserCreate, UserUpdate
from app.utils.migrations import run_migrations
from app.routes import (
    note_routes,
    todo_routes,
    reminder_routes,
    tag_routes,
    public_routes,
    sse,
)


# Set up logging configuration
setup_logging()
logger = get_logger(__name__)
logger.info("Logging configuration completed.")


# Run migrations on startup
run_migrations()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("WORKER_ID") or os.getenv("WORKER_ID") == "0":  # 只在主进程运行        
        ensure_minio_bucket_exists(bucket_name=settings.MINIO_BUCKET)
    print("启动: 创建 Redis 连接池...")
    app.state.auth_redis = await redis_connect()
    yield
    print("关闭: 释放 Redis 连接池...")
    await app.state.auth_redis.aclose()  # type: ignore


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# FastAPI-Users 路由
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/redis", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


app.include_router(note_routes.router)  # Notes Router
app.include_router(todo_routes.router)  # Todos Router
app.include_router(reminder_routes.router)  # Reminders Router
app.include_router(tag_routes.router)  # Tags Router
app.include_router(public_routes.router)  # Public Router
app.include_router(sse.router)  # SSE Router


@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.email}!"}
