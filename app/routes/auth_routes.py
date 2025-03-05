from fastapi import Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.service.user_service import UserService
from app.schemas.schemas import LoginData, Token, UserCreate, UserResponse


logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
) -> Token:
    """Authenticate user and return token."""
    login_data = LoginData(username=form_data.username, password=form_data.password)
    logger.debug(f"Login attempt: {login_data.username}")
    return await UserService(session).authenticate(login_data)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_db)
) -> UserResponse:
    logger.debug(f"Registering user: {user_data.username}")
    new_user = await UserService(session).create_user(user_data)
    return UserResponse.model_validate(new_user)
