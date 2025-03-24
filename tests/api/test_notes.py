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
    response = client.patch(f"/notes/{note_id}", json={"title": "new", "content": "new"})
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
