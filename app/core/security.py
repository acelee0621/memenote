from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password:str, password_hash:str)-> bool:
    return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password:str)->str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None)->str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 JWT 令牌
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get(
            "sub"
        )  # "sub" 是 JWT 的标准字段，通常用于存储主体标识
        if username is None:
            raise credentials_exception        
    except PyJWTError:
        raise credentials_exception
    
    # Import here to avoid circular imports
    from app.core.database import get_db
    from app.service.user_service import UserService

    async for session in get_db():
        user = await UserService(session).get_user_by_username(username)
        if user is None:
            raise credentials_exception
        return user