import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.repository.user_repo import UserRepository
from app.schemas.schemas import UserCreate


@pytest.mark.asyncio
class TestUserRepository:
    async def test_create_user_success(self, db_session: AsyncSession):
        """测试成功创建用户"""
        repo = UserRepository(db_session)
        user_data = UserCreate(
            username="newuser",
            email="new@example.com",
            full_name="New User",
            password="password123"
        )
        
        created_user = await repo.create(user_data)
        
        assert created_user.id is not None
        assert created_user.username == "newuser"
        assert created_user.email == "new@example.com"
        assert created_user.full_name == "New User"
        assert created_user.password_hash is not None

    async def test_create_user_duplicate_username(self, db_session: AsyncSession, test_user):
        """测试创建用户名重复的用户"""
        repo = UserRepository(db_session)
        user_data = UserCreate(
            username="testuser",  # 使用已存在的用户名
            email="new@example.com",
            full_name="New User",
            password="password123"
        )
        
        with pytest.raises(AlreadyExistsException):
            await repo.create(user_data)

    async def test_get_user_by_id_success(self, db_session: AsyncSession, test_user):
        """测试通过ID获取用户"""
        repo = UserRepository(db_session)
        
        retrieved_user = await repo.get_by_id(test_user.id)
        
        assert retrieved_user.id == test_user.id
        assert retrieved_user.username == test_user.username
        assert retrieved_user.email == test_user.email

    async def test_get_user_by_id_not_found(self, db_session: AsyncSession):
        """测试获取不存在的用户"""
        repo = UserRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.get_by_id(9999)

    async def test_get_user_by_username_success(self, db_session: AsyncSession, test_user):
        """测试通过用户名获取用户"""
        repo = UserRepository(db_session)
        
        user = await repo.get_by_username(test_user.username)
        
        assert user is not None
        assert user.username == test_user.username

    async def test_get_user_by_username_not_found(self, db_session: AsyncSession):
        """测试获取不存在的用户名"""
        repo = UserRepository(db_session)
        
        user = await repo.get_by_username("nonexistent")
        
        assert user is None

    async def test_password_hashing_on_create(self, db_session: AsyncSession):
        """测试创建用户时密码被正确哈希(Argon2)"""
        repo = UserRepository(db_session)
        password = "securepassword123"
        user_data = UserCreate(
            username="secureuser",
            email="secure@example.com",
            full_name="Secure User",
            password=password
        )
        
        created_user = await repo.create(user_data)
        
        assert created_user.password_hash != password
        # Argon2 哈希的特征验证
        assert created_user.password_hash.startswith("$argon2")  # Argon2 的标准前缀
        assert len(created_user.password_hash) > 30  # 确保是合理的哈希长度