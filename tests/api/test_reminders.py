from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from app.schemas.schemas import ReminderResponse, NoteResponse


@pytest.mark.parametrize(
    "note_id, expected_status, expected_note_id, message",
    [
        (None, 201, None, "Independent reminder"),  # 独立 reminder
        ("valid", 201, "dynamic", "Reminder under note"),  # 归属 note 的 reminder
        (9999, 404, None, "Reminder with invalid note"),  # 无效 note_id
    ],
    ids=["independent", "under_note", "invalid_note_id"],  # 为每个用例命名
)
def test_create_reminder(
    client: TestClient, mock_user, note_id, expected_status, expected_note_id, message
):
    reminder_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
    # 处理 note_id：如果是 "valid"，动态创建 note
    actual_note_id = note_id
    if note_id == "valid":
        note_resp = client.post(
            "/notes/", json={"title": "Note", "content": "Note content"}
        )
        assert note_resp.status_code == 201
        actual_note_id = note_resp.json()["id"]
    # 发送创建 reminder 的请求
    response = client.post(
        "/reminders/",
        json={"message": message, "reminder_time": reminder_time},
        params={"note_id": actual_note_id} if actual_note_id is not None else {},
    )
    # 验证状态码
    assert response.status_code == expected_status
    # 根据状态码验证响应
    if expected_status == 201:
        reminder = ReminderResponse.model_validate(response.json())
        assert response.json()["reminder_time"] == reminder_time
        assert reminder.message == message
        assert reminder.user_id == mock_user.id
        assert reminder.id is not None
        # 动态验证 note_id
        if expected_note_id == "dynamic":
            assert reminder.note_id == actual_note_id
        else:
            assert reminder.note_id == expected_note_id
    elif expected_status == 404:
        assert "Note with id 9999 not found" in response.text
