from datetime import datetime, timezone
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_login_success(client: TestClient, mocker):
    # Mock UserService
    mock_user_service = mocker.patch("app.routes.auth_routes.UserService")
    # 配置 authenticate 为异步方法，返回 dict
    mock_user_service.return_value.authenticate = AsyncMock(return_value={"access_token": "fake_token", "token_type": "bearer"})
    
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "test123"}
    )
    assert response.status_code == 200
    assert response.json() == {"access_token": "fake_token", "token_type": "bearer"}

@pytest.mark.asyncio
async def test_login_failure(client: TestClient, mocker):
    mock_user_service = mocker.patch("app.routes.auth_routes.UserService")
    # 配置 authenticate 抛出异常
    mock_user_service.return_value.authenticate = AsyncMock(side_effect=HTTPException(
        status_code=401, detail="Incorrect username or password"
    ))
    
    response = client.post(
        "/auth/login",
        data={"username": "wronguser", "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_success(client: TestClient, mocker):
    # 创建 Mock 用户，设置所有字段
    mock_user = mocker.Mock()
    mock_user.id = 1
    mock_user.username = "newuser"
    mock_user.email = "newuser@example.com"
    mock_user.full_name = "New User"
    mock_user.created_at = datetime.now(timezone.utc)
    mock_user.updated_at = datetime.now(timezone.utc)
    
    mock_user_service = mocker.patch("app.routes.auth_routes.UserService")
    mock_user_service.return_value.create_user = AsyncMock(return_value=mock_user)
    
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "newpass123"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert response.json()["id"] == 1
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["full_name"] == "New User"

@pytest.mark.asyncio
async def test_register_username_exists(client: TestClient, mocker):
    mock_user_service = mocker.patch("app.routes.auth_routes.UserService")
    # 配置 create_user 抛出异常
    mock_user_service.return_value.create_user = AsyncMock(side_effect=HTTPException(
        status_code=400, detail="Username already registered"
    ))
    
    response = client.post(
        "/auth/register",
        json={"username": "existinguser", "password": "test123"}
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]