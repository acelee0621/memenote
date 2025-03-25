from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.schemas.schemas import NoteResponse


def test_create_note(client: TestClient, mock_user):
    response = client.post(
        "/notes/",
        json={"title": "test note", "content": "test note content"},
    )
    # 断言响应状态码和数据
    assert response.status_code == 201
    note = NoteResponse.model_validate(response.json())
    assert note.id is not None
    assert note.title == "test note"
    assert note.content == "test note content"
    assert note.user_id == mock_user.id


def test_get_note(client):
    # 先创建
    create_resp = client.post(
        "/notes/", json={"title": "test note", "content": "test content"}
    )
    note_id = create_resp.json()["id"]
    # 再获取
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    note = NoteResponse.model_validate(response.json())
    assert note.id == note_id


def test_update_note(client):
    create_resp = client.post("/notes/", json={"title": "old", "content": "old"})
    note_id = create_resp.json()["id"]
    response = client.patch(
        f"/notes/{note_id}", json={"title": "new", "content": "new"}
    )
    assert response.status_code == 200
    note = NoteResponse.model_validate(response.json())
    assert note.title == "new"


def test_delete_note(client):
    create_resp = client.post("/notes/", json={"title": "test", "content": "test"})
    note_id = create_resp.json()["id"]
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204
    get_resp = client.get(f"/notes/{note_id}")
    assert get_resp.status_code == 404


def test_get_all_notes_empty(client: TestClient, mock_user):
    response = client.get("/notes/")
    assert response.status_code == 200
    assert response.json() == []  # 初始无笔记


def test_get_all_notes_with_data(client: TestClient, mock_user):
    # 创建多个笔记
    client.post("/notes/", json={"title": "note1", "content": "content1"})
    client.post("/notes/", json={"title": "note2", "content": "content2"})
    response = client.get("/notes/")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 2
    assert notes[0]["title"] == "note1"
    assert notes[1]["title"] == "note2"


def test_get_all_notes_with_query_params(client: TestClient, mock_user):
    # 创建测试数据
    client.post("/notes/", json={"title": "apple note", "content": "fruit"})
    client.post("/notes/", json={"title": "banana note", "content": "yellow"})
    # 测试 search
    response = client.get("/notes/?search=apple")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "apple note"
    # 测试 limit
    response = client.get("/notes/?offset=0&limit=1")
    assert len(response.json()) == 1


def test_create_note_failure(client: TestClient, mocker, mock_user):
    # 模拟抛出 HTTPException 而不是普通 Exception
    mocker.patch(
        "app.service.note_service.NoteService.create_note",
        side_effect=HTTPException(status_code=500, detail="Database error"),
    )
    response = client.post("/notes/", json={"title": "test", "content": "test"})
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]


def test_get_note_not_found(client: TestClient, mock_user):
    response = client.get("/notes/999")
    assert response.status_code == 404  # 假设服务抛出 404


def test_update_note_not_found(client: TestClient, mock_user):
    response = client.patch("/notes/999", json={"title": "new"})
    assert response.status_code == 404


def test_delete_note_not_found(client: TestClient, mock_user):
    response = client.delete("/notes/999")
    assert response.status_code == 404


def test_unauthorized_access(non_auth_client: TestClient):
    # 不设置认证头
    non_auth_client.headers.pop("Authorization", None)
    response = non_auth_client.post(
        "/notes/", json={"title": "test", "content": "test"}
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_create_note_long_title(client: TestClient, mock_user):
    long_title = "a" * 256  # 假设最大长度 255
    response = client.post("/notes/", json={"title": long_title, "content": "test"})
    assert response.status_code == 422  # 假设有长度限制
