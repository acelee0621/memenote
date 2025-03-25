import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from datetime import datetime

@pytest.mark.asyncio
async def test_create_reminder_triggers_celery_tasks(client: TestClient, mock_user):
    with patch("app.service.reminder_service.celery_app.send_task") as mock_send_task:
        reminder_time = "2025-03-25T15:16:00Z"
        response = client.post(
            "/reminders/",
            json={"message": "Test reminder", "reminder_time": reminder_time}
        )
        assert response.status_code == 201
        reminder_id = response.json()["id"]

        # 验证调用次数
        assert mock_send_task.call_count == 2

        # 验证第一次调用（通知任务）
        notify_call = mock_send_task.call_args_list[0]
        assert notify_call[0][0] == "app.tasks.reminder_task.notify_reminder_action"
        assert notify_call[1]["task_id"] == f"notify_reminder_create_{reminder_id}"

        # 验证第二次调用（触发任务）
        trigger_call = mock_send_task.call_args_list[1]
        assert trigger_call[0][0] == "app.tasks.reminder_task.trigger_reminder"
        assert trigger_call[1]["task_id"] == f"trigger_reminder_{reminder_id}"
        assert trigger_call[1]["eta"] == datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))