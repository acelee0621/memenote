import pytest
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from unittest.mock import AsyncMock
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.core.config import settings

# 模拟 get_db 的异步生成器
async def mock_get_db(db_session):
    yield db_session

def test_verify_password():
    plain_password = "test123"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed_password) is True
    assert verify_password("wrong", hashed_password) is False

def test_get_password_hash():
    password = "test123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded

@pytest.mark.asyncio
async def test_get_current_user_valid_token(mocker, db_session):
    token = create_access_token({"sub": "testuser"})
    mock_user = mocker.Mock(username="testuser", id=1)
    mock_service = mocker.patch("app.service.user_service.UserService")
    mock_service.return_value.get_user_by_username = AsyncMock(return_value=mock_user)
    mocker.patch("app.core.database.get_db", return_value=mock_get_db(db_session))
    user = await get_current_user(token)
    assert user.username == "testuser"
    assert user.id == 1

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session, mocker):
    mocker.patch("app.core.database.get_db", return_value=mock_get_db(db_session))
    with pytest.raises(HTTPException) as exc:
        await get_current_user("invalid_token")
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_expired_token(db_session, mocker):
    expired_token = create_access_token({"sub": "testuser"}, expires_delta=timedelta(minutes=-1))
    mocker.patch("app.core.database.get_db", return_value=mock_get_db(db_session))
    with pytest.raises(HTTPException) as exc:
        await get_current_user(expired_token)
    assert exc.value.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mocker, db_session):
    token = create_access_token({"sub": "testuser"})
    mock_service = mocker.patch("app.service.user_service.UserService")
    mock_service.return_value.get_user_by_username = AsyncMock(return_value=None)
    mocker.patch("app.core.database.get_db", return_value=mock_get_db(db_session))
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token)
    assert exc.value.status_code == 401
    
@pytest.mark.filterwarnings("ignore:Accessing argon2.__version__:DeprecationWarning")
def test_verify_password():
    plain_password = "test123"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed_password) is True
    assert verify_password("wrong", hashed_password) is False