import asyncio
import json

from fastapi import APIRouter
from fastapi.websockets import WebSocket
import redis.asyncio as redis


connected_clients = set()
redis_client = redis.Redis(host="localhost", port=6379, db=0)

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("reminder_notifications")  # 监听多个频道
        
        async def listen_redis():
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = json.loads(message["data"].decode())
                    for client in connected_clients:
                        await client.send_json(data)
                await asyncio.sleep(0.01)
        
        asyncio.create_task(listen_redis())
        while True:
            await websocket.receive_text()  # 保持连接
    except Exception:
        connected_clients.remove(websocket)
        await pubsub.unsubscribe("reminder_notifications")
        
        
router = APIRouter(tags=["WebSocket"])
@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket_endpoint(websocket)