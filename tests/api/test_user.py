from fastapi.testclient import TestClient# from tests.conftest import client
from app.schemas.schemas import UserResponse


def test_users_me(client: TestClient, mock_user):    
    response = client.get("/users/me")
    assert response.status_code == 200
    user_response = UserResponse.model_validate(response.json())

    assert user_response == mock_user
