import os
import asyncio
import json
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as redis


router = APIRouter(tags=["SSE"])

redis_host = os.getenv("REDIS_HOST", "localhost:6379")
REDIS_URL = f"redis://{redis_host}/0"

# current_user: UserResponse = Depends(get_current_user)
redis_client = redis.from_url(
    REDIS_URL,
    health_check_interval=30,
)


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
                        "data": json.dumps(data, ensure_ascii=False),
                    }
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"SSE error: {e}")
        finally:
            await pubsub.unsubscribe(channel)
            print(f"SSE unsubscribed from {channel}")

    return EventSourceResponse(event_generator())