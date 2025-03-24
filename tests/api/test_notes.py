import pytest

from app.main import app
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import NoteResponse

# 从 conftest.py 中导入 fixture
from tests.conftest import client, mock_user, override_get_db

@pytest.mark.asyncio
async def test_create_note(override_get_db, mock_user):
    """
    测试创建笔记的功能。
    """
    # 覆盖 get_db 和 get_current_user 依赖项
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # 发送创建笔记的请求
    response = client.post(
        "/notes/",
        json={"title": "test note", "content": "test note content"},
    )

    # 断言响应状态码和数据
    assert response.status_code == 201
    note_response = NoteResponse.model_validate(response.json())    
    
    assert note_response.id == 1
    assert note_response.title == "test note"
    assert note_response.content == "test note content"
    assert note_response.user_id == mock_user.id
    assert note_response.reminders == []
    assert note_response.todos == []

    # 清理依赖项覆盖
    app.dependency_overrides.clear()