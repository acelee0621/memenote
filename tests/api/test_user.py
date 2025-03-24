import pytest
from tests.conftest import client
from app.main import app

from app.core.security import get_current_user
from app.schemas.schemas import UserResponse



# 测试users/me路由
@pytest.mark.asyncio
async def test_users_me(mock_user):
    # 覆盖 get_current_user 依赖项，确保测试时不需要真正的认证
    app.dependency_overrides[get_current_user] = lambda: mock_user
    response = client.get("/users/me")
    assert response.status_code == 200
    user_response = UserResponse.model_validate(response.json())
    # assert response.json() == {
    #     "id": 777,
    #     "username": "testuser",
    #     "full_name": "Test User",
    #     "email": "test@example.com",
    #     "created_at": "2023-10-01T00:00:00Z",
    #     "updated_at": "2023-10-01T00:00:00Z",
    # }
    assert user_response == mock_user
    
    app.dependency_overrides.clear()
    

