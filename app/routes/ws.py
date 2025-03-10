import asyncio
import json

from fastapi import APIRouter, WebSocketDisconnect
from fastapi.websockets import WebSocket
import redis.asyncio as redis


router = APIRouter(tags=["WebSocket"])

# 全局变量
connected_clients = set()
redis_client = redis.Redis(host="localhost", port=6379, db=0)
REDIS_CHANNEL = "reminder_notifications"


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"WebSocket client connected. Total clients: {len(connected_clients)}")

    try:
        # 创建Redis PubSub对象
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(REDIS_CHANNEL)
        print(f"WebSocket subscribed to {REDIS_CHANNEL}")

        # 创建Redis监听任务
        async def listen_redis():
            try:
                while True:
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
                    if message:
                        data = json.loads(message["data"].decode())
                        for client in connected_clients:
                            try:
                                await client.send_json(data)
                            except Exception as e:
                                print(f"Error sending to client: {e}")
                                # 出错的客户端可能已断开，但我们在外层循环处理断开连接
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                # 正常取消任务的情况
                print("Redis listener task cancelled")
            except Exception as e:
                print(f"Redis listener error: {e}")

        # 启动监听任务
        listen_task = asyncio.create_task(listen_redis())

        # 保持WebSocket连接
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        print("WebSocket client disconnected normally")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # 清理资源
        if websocket in connected_clients:
            connected_clients.remove(websocket)

        try:
            await pubsub.unsubscribe(REDIS_CHANNEL)
        except Exception as e:
            print(f"Error unsubscribing from Redis: {e}")

        if "listen_task" in locals():
            if not listen_task.done():
                listen_task.cancel()

            try:
                await asyncio.shield(listen_task)
            except asyncio.CancelledError:
                pass

        print(
            f"WebSocket cleanup completed. Remaining clients: {len(connected_clients)}"
        )


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket_endpoint(websocket)
