import pytest
from fastapi.testclient import TestClient
from app.schemas.schemas import NoteResponse


@pytest.mark.asyncio
async def test_create_note(client: TestClient, mock_user): 
    response = client.post(
        "/notes/",
        json={"title": "test note", "content": "test note content"},
    )

    # 断言响应状态码和数据
    assert response.status_code == 201
    note_response = NoteResponse.model_validate(response.json())

    assert note_response.id is not None
    assert note_response.title == "test note"
    assert note_response.content == "test note content"
    assert note_response.user_id == mock_user.id
    assert note_response.reminders == []
    assert note_response.todos == []
