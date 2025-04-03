import pytest
from httpx import AsyncClient
from app.schemas.schemas import UserResponse


@pytest.mark.filterwarnings("ignore:Accessing argon2.__version__:DeprecationWarning")
@pytest.mark.asyncio
async def test_users_me(authorized_client: AsyncClient, test_user: UserResponse):
    response = await authorized_client.get("/users/me")
    assert response.status_code == 200
    user_response = UserResponse.model_validate(response.json())
    
    assert user_response == test_user
    assert "password_hash" not in response.json()
