from fastapi import Depends, APIRouter

from app.core.logging import get_logger
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import UserResponse


logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse.model_validate(user)
