from typing import Optional

from fastapi import Depends, Request
from redis.asyncio import Redis
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    RedisStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from app.core.config import settings
from app.core.database import User, get_user_db
from app.core.redis_db import get_auth_redis
from app.core.celery_app import celery_app

SECRET = settings.JWT_SECRET


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        celery_app.send_task(
            "app.tasks.mail_task.register_email",
            args=[user],
            task_id=f"register_email_sent_{user.id}",
        )

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/redis/login")


def get_redis_strategy(auth_redis: Redis = Depends(get_auth_redis)) -> RedisStrategy:
    return RedisStrategy(auth_redis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

get_current_user = fastapi_users.current_user(active=True)

""" 以下为不同的获取当前用户的策略，可根据需要选择 """
# 获取当前激活用户
current_active_user = fastapi_users.current_user(active=True)
# 获取当前激活且已验证用户
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
# 获取当前激活且为超级用户
current_superuser = fastapi_users.current_user(active=True, superuser=True)
