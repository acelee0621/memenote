import asyncio
import json
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as redis

from app.core.security import get_current_user
from app.schemas.schemas import UserResponse

router = APIRouter(tags=["SSE"])

redis_client = redis.Redis(host="localhost", port=6379, db=0)
# current_user: UserResponse = Depends(get_current_user)


@router.get("/notifications/stream")
async def notification_stream():
    """
    SSE endpoint to stream reminder notifications for a specific user.
    """

    async def event_generator():
        pubsub = redis_client.pubsub()
        # channel = f"reminder_notifications_{current_user.id}"  # 用户专属频道
        channel = "reminder_notifications"
        await pubsub.subscribe(channel)
        print(f"SSE subscribed to {channel}")

        try:
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message:
                    data = json.loads(message["data"].decode("utf-8"))
                    print(f"SSE sending: {data}")
                    yield {
                        "event": "notification",
                        "data": json.dumps(data),  # 客户端接收 JSON 字符串
                    }
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"SSE error: {e}")
        finally:
            await pubsub.unsubscribe(channel)
            print(f"SSE unsubscribed from {channel}")

    return EventSourceResponse(event_generator())
