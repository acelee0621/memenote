import os
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.s3_client import ensure_minio_bucket_exists
from app.utils.migrations import run_migrations

from app.routes import (
    user_routes,
    note_routes,
    todo_routes,
    reminder_routes,
    auth_routes,
    tag_routes,
    public_routes,
    sse,
)


# Set up logging configuration
setup_logging()
logger = get_logger(__name__)
logger.info("Logging configuration completed.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("WORKER_ID") or os.getenv("WORKER_ID") == "0":  # 只在主进程运行
        run_migrations()  # Run migrations on startup
        ensure_minio_bucket_exists(bucket_name=settings.MINIO_BUCKET)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_routes.router)  # Auth Router
app.include_router(user_routes.router)  # Users Router
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
