import pytest
import httpx
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, UTC
import asyncio

from app.main import app


@pytest.mark.asyncio
async def test_create_reminder_sends_sse_notification(client: TestClient, mock_user):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url="http://test") as async_client:
        # 假设服务器运行在 TestClient 的上下文中
        async with async_client.stream("GET", f"/sse/notifications?user_id={mock_user.id}") as sse_response:
            reminder_time = (datetime.now(UTC) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
            create_response = client.post(
                "/reminders/",
                json={"message": "SSE Test", "reminder_time": reminder_time}
            )
            assert create_response.status_code == 201
            reminder_id = create_response.json()["id"]

            async with asyncio.timeout(5):
                async for event in sse_response.aiter_lines():
                    if "data" in event:
                        data = event.split("data: ")[1]
                        assert str(reminder_id) in data
                        break