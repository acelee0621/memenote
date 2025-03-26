import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.models import Todo
from app.repository.todo_repo import TodoRepository
from app.schemas.schemas import TodoCreate, TodoUpdate


@pytest.mark.asyncio
class TestTodoRepository:
    async def test_create_todo_success(self, db_session: AsyncSession, test_user):
        """测试成功创建Todo"""
        repo = TodoRepository(db_session)
        todo_data = TodoCreate(content="Test Todo Content")
        
        created_todo = await repo.create(todo_data, None, test_user)
        
        assert created_todo.id is not None
        assert created_todo.content == "Test Todo Content"
        assert created_todo.user_id == test_user.id
        assert created_todo.note_id is None

    async def test_create_todo_with_note(self, db_session: AsyncSession, test_user, test_note):
        """测试创建关联到Note的Todo"""
        repo = TodoRepository(db_session)
        todo_data = TodoCreate(content="Todo with note")
        
        created_todo = await repo.create(todo_data, test_note.id, test_user)
        
        assert created_todo.note_id == test_note.id

    async def test_get_todo_by_id_success(self, db_session: AsyncSession, test_user, test_todo):
        """测试通过ID获取Todo"""
        repo = TodoRepository(db_session)
        
        retrieved_todo = await repo.get_by_id(test_todo.id, test_user)
        
        assert retrieved_todo.id == test_todo.id
        assert retrieved_todo.content == test_todo.content

    async def test_get_todo_by_id_not_found(self, db_session: AsyncSession, test_user):
        """测试获取不存在的Todo"""
        repo = TodoRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.get_by_id(9999, test_user)

    async def test_get_todo_by_id_wrong_user(self, db_session: AsyncSession, test_user, another_user, test_todo):
        """测试获取不属于当前用户的Todo"""
        repo = TodoRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.get_by_id(test_todo.id, another_user)

    async def test_get_all_todos_empty(self, db_session: AsyncSession, test_user):
        """测试获取空Todo列表"""
        repo = TodoRepository(db_session)
        
        todos = await repo.get_all(None, None, None, None, test_user)
        
        assert len(todos) == 0

    async def test_get_all_todos_with_data(self, db_session: AsyncSession, test_user, multiple_test_todos):
        """测试获取所有Todo"""
        repo = TodoRepository(db_session)
        
        todos = await repo.get_all(None, None, None, None, test_user)
        
        assert len(todos) == len(multiple_test_todos)
        assert all(todo.user_id == test_user.id for todo in todos)

    async def test_get_all_todos_with_note_filter(self, db_session: AsyncSession, test_user, test_note):
        """测试按Note ID过滤Todo"""
        repo = TodoRepository(db_session)
        
        # 创建3个Todo，其中2个关联到test_note
        todo1 = Todo(content="Todo 1", user_id=test_user.id, note_id=test_note.id)
        todo2 = Todo(content="Todo 2", user_id=test_user.id, note_id=test_note.id)
        todo3 = Todo(content="Todo 3", user_id=test_user.id)
        db_session.add_all([todo1, todo2, todo3])
        await db_session.commit()
        
        # 查询关联到note的todos
        todos = await repo.get_all(test_note.id, None, None, None, test_user)
        assert len(todos) == 2
        assert all(todo.note_id == test_note.id for todo in todos)

    async def test_get_all_todos_with_status_filter(self, db_session: AsyncSession, test_user):
        """测试按状态过滤Todo"""
        repo = TodoRepository(db_session)
        
        # 创建测试数据
        todo1 = Todo(content="Todo 1", user_id=test_user.id, is_completed=True)
        todo2 = Todo(content="Todo 2", user_id=test_user.id, is_completed=False)
        db_session.add_all([todo1, todo2])
        await db_session.commit()
        
        # 测试已完成
        completed = await repo.get_all(None, "finished", None, None, test_user)
        assert len(completed) == 1
        assert completed[0].is_completed is True
        
        # 测试未完成
        uncompleted = await repo.get_all(None, "unfinished", None, None, test_user)
        assert len(uncompleted) == 1
        assert uncompleted[0].is_completed is False

    async def test_get_all_todos_with_search(self, db_session: AsyncSession, test_user):
        """测试搜索Todo内容"""
        repo = TodoRepository(db_session)
        
        # 创建测试数据
        todo1 = Todo(content="Buy milk", user_id=test_user.id)
        todo2 = Todo(content="Read book", user_id=test_user.id)
        db_session.add_all([todo1, todo2])
        await db_session.commit()
        
        # 搜索
        results = await repo.get_all(None, None, "milk", None, test_user)
        assert len(results) == 1
        assert "milk" in results[0].content.lower()

    async def test_get_all_todos_with_ordering(self, db_session: AsyncSession, test_user):
        """测试Todo排序"""
        repo = TodoRepository(db_session)
        
        # 创建测试数据
        todo1 = Todo(content="A", user_id=test_user.id)
        todo2 = Todo(content="B", user_id=test_user.id)
        db_session.add_all([todo1, todo2])
        await db_session.commit()
        
        # 升序
        asc_todos = await repo.get_all(None, None, None, "created_at asc", test_user)
        assert asc_todos[0].content == "A"
        
        # 降序
        desc_todos = await repo.get_all(None, None, None, "created_at desc", test_user)
        assert desc_todos[0].content == "B"

    async def test_update_todo_success(self, db_session: AsyncSession, test_user, test_todo):
        """测试成功更新Todo"""
        repo = TodoRepository(db_session)
        update_data = TodoUpdate(content="Updated content", is_completed=True)
        
        updated_todo = await repo.update(update_data, test_todo.id, test_user)
        
        assert updated_todo.content == "Updated content"
        assert updated_todo.is_completed is True

    async def test_update_todo_partial(self, db_session: AsyncSession, test_user, test_todo):
        """测试部分更新Todo"""
        repo = TodoRepository(db_session)
        original_content = test_todo.content
        update_data = TodoUpdate(is_completed=True)
        
        updated_todo = await repo.update(update_data, test_todo.id, test_user)
        
        assert updated_todo.content == original_content  # 内容未改变
        assert updated_todo.is_completed is True  # 仅更新完成状态

    async def test_update_todo_not_found(self, db_session: AsyncSession, test_user):
        """测试更新不存在的Todo"""
        repo = TodoRepository(db_session)
        update_data = TodoUpdate(content="Updated")
        
        with pytest.raises(NotFoundException):
            await repo.update(update_data, 9999, test_user)

    async def test_update_todo_no_fields(self, db_session: AsyncSession, test_user, test_todo):
        """测试没有提供更新字段的情况"""
        repo = TodoRepository(db_session)
        update_data = TodoUpdate()
        
        with pytest.raises(ValueError, match="No fields to update"):
            await repo.update(update_data, test_todo.id, test_user)

    async def test_delete_todo_success(self, db_session: AsyncSession, test_user, test_todo):
        """测试成功删除Todo"""
        repo = TodoRepository(db_session)
        
        await repo.delete(test_todo.id, test_user)
        
        # 验证Todo已被删除
        with pytest.raises(NotFoundException):
            await repo.get_by_id(test_todo.id, test_user)

    async def test_delete_todo_not_found(self, db_session: AsyncSession, test_user):
        """测试删除不存在的Todo"""
        repo = TodoRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.delete(9999, test_user)

    async def test_delete_todo_wrong_user(self, db_session: AsyncSession, test_user, another_user, test_todo):
        """测试删除不属于当前用户的Todo"""
        repo = TodoRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.delete(test_todo.id, another_user)