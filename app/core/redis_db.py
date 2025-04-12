from fastapi import Request
from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings


auth_pool = ConnectionPool.from_url(
    f"redis://{settings.REDIS_HOST}", db=2, max_connections=10, decode_responses=True
)


async def redis_connect():
    try:
        redis_client = Redis(connection_pool=auth_pool)
        is_connected = await redis_client.ping()
        if is_connected:
            print("redis连接成功")
        return redis_client
    except ConnectionError:
        print("redis连接失败")
    except TimeoutError:
        print("redis连接超时")
    except Exception as e:
        print("redis连接异常", e)


async def get_auth_redis(request: Request) -> Redis:
    return request.app.state.auth_redis
