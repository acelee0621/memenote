from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from app.schemas.schemas import ReminderResponse, NoteResponse


reminder_time = (
    (datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
)


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


# 测试获取某个 note 下的 reminders
def test_get_reminders_for_note(client: TestClient):
    # 创建 note
    note_response = client.post(
        "/notes/", json={"title": "Test Note", "content": "Note content"}
    )
    assert note_response.status_code == 201
    note = NoteResponse.model_validate(note_response.json())
    note_id = note.id

    # 创建两个关联 reminders
    client.post(
        "/reminders/",
        json={"message": "Reminder 1", "reminder_time": reminder_time},
        params={"note_id": note_id},
    )
    client.post(
        "/reminders/",
        json={"message": "Reminder 2", "reminder_time": reminder_time},
        params={"note_id": note_id},
    )
    # 创建一个独立 reminder
    client.post(
        "/reminders/",
        json={"message": "Independent Reminder", "reminder_time": reminder_time},
    )

    # 获取该 note 下的 reminders
    response = client.get(f"/reminders?note_id={note_id}")
    assert response.status_code == 200
    reminders = [
        ReminderResponse.model_validate(reminder) for reminder in response.json()
    ]

    # 验证
    assert len(reminders) == 2
    assert all(reminder.note_id == note_id for reminder in reminders)
    assert {reminder.message for reminder in reminders} == {"Reminder 1", "Reminder 2"}


# 测试获取所有 reminders（无过滤）
def test_get_all_reminders(client: TestClient):
    client.post(
        "/reminders/", json={"message": "Reminder 1", "reminder_time": reminder_time}
    )
    client.post(
        "/reminders/", json={"message": "Reminder 2", "reminder_time": reminder_time}
    )
    response = client.get("/reminders/")
    assert response.status_code == 200
    reminders = [
        ReminderResponse.model_validate(reminder) for reminder in response.json()
    ]
    assert len(reminders) >= 2
    assert any(reminder.message == "Reminder 1" for reminder in reminders)


# 测试获取单个 reminder
def test_get_reminder_by_id(client: TestClient):
    create_response = client.post(
        "/reminders/", json={"message": "Test Reminder", "reminder_time": reminder_time}
    )
    assert create_response.status_code == 201
    reminder_id = create_response.json()["id"]
    response = client.get(f"/reminders/{reminder_id}")
    assert response.status_code == 200
    reminder = ReminderResponse.model_validate(response.json())
    assert reminder.id == reminder_id
    assert reminder.message == "Test Reminder"


# 测试更新 reminder
def test_update_reminder(client: TestClient):
    create_response = client.post(
        "/reminders/", json={"message": "Old Reminder", "reminder_time": reminder_time}
    )
    assert create_response.status_code == 201
    reminder_id = create_response.json()["id"]
    response = client.patch(
        f"/reminders/{reminder_id}", json={"message": "New Reminder"}
    )
    assert response.status_code == 200
    updated_reminder = ReminderResponse.model_validate(response.json())
    assert updated_reminder.id == reminder_id
    assert updated_reminder.message == "New Reminder"


# 测试删除 reminder
def test_delete_reminder(client: TestClient):
    create_response = client.post(
        "/reminders/",
        json={"message": "Reminder to delete", "reminder_time": reminder_time},
    )
    assert create_response.status_code == 201
    reminder_id = create_response.json()["id"]
    response = client.delete(f"/reminders/{reminder_id}")
    assert response.status_code == 204
    get_response = client.get(f"/reminders/{reminder_id}")
    assert get_response.status_code == 404


# 测试无效 note_id
def test_get_reminders_with_invalid_note_id(client: TestClient):
    response = client.get("/reminders?note_id=9999")
    assert response.status_code == 404


# 测试 search 过滤
def test_get_reminders_by_search(client: TestClient):
    client.post(
        "/reminders/",
        json={"message": "Searchable Reminder", "reminder_time": reminder_time},
    )
    client.post(
        "/reminders/",
        json={"message": "Other Reminder", "reminder_time": reminder_time},
    )
    response = client.get("/reminders?search=Searchable")
    assert response.status_code == 200
    reminders = [
        ReminderResponse.model_validate(reminder) for reminder in response.json()
    ]
    assert len(reminders) == 1
    assert reminders[0].message == "Searchable Reminder"


# 测试 order_by 过滤
def test_get_reminders_by_order(client: TestClient):
    client.post(
        "/reminders/",
        json={"message": "First Reminder", "reminder_time": reminder_time},
    )
    client.post(
        "/reminders/",
        json={"message": "Second Reminder", "reminder_time": reminder_time},
    )
    response = client.get("/reminders?order_by=created_at asc")
    assert response.status_code == 200
    reminders = [
        ReminderResponse.model_validate(reminder) for reminder in response.json()
    ]
    assert len(reminders) == 2
    assert reminders[0].message == "First Reminder"
