from httpx import AsyncClient
import pytest
from fastapi import HTTPException
from app.schemas.schemas import NoteResponse


@pytest.mark.asyncio
async def test_create_note(authorized_client:AsyncClient, test_user):
    response = await authorized_client.post(
        "/notes",
        json={"title": "test note", "content": "test note content"},
    )
    # 断言响应状态码和数据
    assert response.status_code == 201
    note = NoteResponse.model_validate(response.json())
    assert note.id is not None
    assert note.title == "test note"
    assert note.content == "test note content"
    assert note.user_id == test_user.id


@pytest.mark.asyncio
async def test_get_note(authorized_client:AsyncClient):
    # 先创建
    create_resp = await authorized_client.post(
        "/notes", json={"title": "test note", "content": "test content"}
    )
    note_id = create_resp.json()["id"]
    # 再获取
    response = await authorized_client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    note = NoteResponse.model_validate(response.json())
    assert note.id == note_id


@pytest.mark.asyncio
async def test_update_note(authorized_client:AsyncClient):
    create_resp = await authorized_client.post("/notes", json={"title": "old", "content": "old"})
    note_id = create_resp.json()["id"]
    response = await authorized_client.patch(
        f"/notes/{note_id}", json={"title": "new", "content": "new"}
    )
    assert response.status_code == 200
    note = NoteResponse.model_validate(response.json())
    assert note.title == "new"


@pytest.mark.asyncio
async def test_delete_note(authorized_client:AsyncClient):
    create_resp = await authorized_client.post("/notes", json={"title": "test", "content": "test"})
    note_id = create_resp.json()["id"]
    assert note_id is not None
    response = await authorized_client.delete(f"/notes/{note_id}")
    assert response.status_code == 204
    get_resp = await authorized_client.get(f"/notes/{note_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_all_notes_empty(authorized_client:AsyncClient):
    response = await authorized_client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_all_notes_with_data(authorized_client:AsyncClient):
    # 创建多个笔记
    await authorized_client.post("/notes", json={"title": "note1", "content": "content1"})
    await authorized_client.post("/notes", json={"title": "note2", "content": "content2"})
    response = await authorized_client.get("/notes")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 2
    assert notes[0]["title"] == "note1"
    assert notes[1]["title"] == "note2"


@pytest.mark.asyncio
async def test_get_all_notes_with_query_params(authorized_client:AsyncClient):
    # 创建测试数据
    await authorized_client.post("/notes", json={"title": "apple note", "content": "fruit"})
    await authorized_client.post("/notes", json={"title": "banana note", "content": "yellow"})
    # 测试 search
    response = await authorized_client.get("/notes?search=apple")
    assert response.status_code == 200
    notes = response.json()
    assert len(notes) == 1
    assert notes[0]["title"] == "apple note"
    # 测试 limit
    response = await authorized_client.get("/notes?offset=0&limit=1")
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_create_note_failure(authorized_client:AsyncClient, mocker):
    # 模拟抛出 HTTPException 而不是普通 Exception
    mocker.patch(
        "app.service.note_service.NoteService.create_note",
        side_effect=HTTPException(status_code=500, detail="Database error"),
    )
    response = await authorized_client.post("/notes", json={"title": "test", "content": "test"})
    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_note_not_found(authorized_client:AsyncClient):
    response = await authorized_client.get("/notes/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_note_not_found(authorized_client:AsyncClient):
    response = await authorized_client.patch("/notes/999", json={"title": "new"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_note_not_found(authorized_client:AsyncClient):
    response = await authorized_client.delete("/notes/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(unauthorized_client:AsyncClient):    
    response = await unauthorized_client.post(
        "/notes", json={"title": "test", "content": "test"}
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_note_long_title(authorized_client:AsyncClient):
    long_title = "a" * 256
    response = await authorized_client.post("/notes", json={"title": long_title, "content": "test"})
    assert response.status_code == 422 
