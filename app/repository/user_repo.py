from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.core.logging import get_logger
from app.core.security import get_password_hash
from app.models.models import User
from app.schemas.schemas import UserCreate


logger = get_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_data (UserCreate): Data for the new user.

        Returns:
            UserInDB: The newly created user.

        Raises:
            AlreadyExistsException: If the username already exists.
        """
        # Check if user exists
        existing_user = await self.get_by_username(user_data.username)
        if existing_user:
            raise AlreadyExistsException("Username already registered")
        # Create user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=get_password_hash(user_data.password),  # 加密密码
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        logger.info(f"Created user: {new_user.username}")
        return new_user

    async def get_by_id(self, user_id: int) -> User:
        """
        Get a user by ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            UserResponse: The user if found.

        Raises:
            NotFoundException: If the user is not found.
        """

        query = select(User).where(User.id == user_id)
        result = await self.session.scalars(query)
        user = result.one_or_none()
        if not user:
            raise NotFoundException("User not found")
        return user

    async def get_by_username(self, username: str) -> User | None:
        """
        Get a user by username.

        Args:
            username (str): The username to search for.

        Returns:
            UserInDB | None: The user if found, otherwise None.
        """
        query = select(User).where(User.username == username)
        result = await self.session.scalars(query)
        user = result.one_or_none()
        return user
