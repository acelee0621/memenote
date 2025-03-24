import pytest
from fastapi.testclient import TestClient# from tests.conftest import client
from app.schemas.schemas import UserResponse


# 测试users/me路由
@pytest.mark.asyncio
async def test_users_me(client: TestClient, mock_user):
    # 覆盖 get_current_user 依赖项，确保测试时不需要真正的认证
    # app.dependency_overrides[get_current_user] = lambda: mock_user
    response = client.get("/users/me")
    assert response.status_code == 200
    user_response = UserResponse.model_validate(response.json())

    assert user_response == mock_user
