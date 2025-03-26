import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.models import Note
from app.repository.note_repo import NoteRepository
from app.schemas.schemas import NoteCreate, NoteUpdate


@pytest.mark.asyncio
class TestNoteRepository:
    async def test_create_note_success(self, db_session: AsyncSession, test_user):
        """测试成功创建笔记"""
        repo = NoteRepository(db_session)
        note_data = NoteCreate(title="Test Note", content="This is a test note")
        
        created_note = await repo.create(note_data, test_user)
        
        assert created_note.id is not None
        assert created_note.title == "Test Note"
        assert created_note.content == "This is a test note"
        assert created_note.user_id == test_user.id

    async def test_create_note_duplicate_content(self, db_session: AsyncSession, test_user):
        """测试创建内容重复的笔记"""
        repo = NoteRepository(db_session)
        note_data = NoteCreate(title="Test Note", content="Duplicate content")
        
        # 第一次创建应该成功
        await repo.create(note_data, test_user)
        
        # 第二次创建相同内容应该失败
        with pytest.raises(AlreadyExistsException):
            await repo.create(note_data, test_user)

    async def test_get_note_by_id_success(self, db_session: AsyncSession, test_user, test_note):
        """测试通过ID获取笔记"""
        repo = NoteRepository(db_session)
        
        retrieved_note = await repo.get_by_id(test_note.id, test_user)
        
        assert retrieved_note.id == test_note.id
        assert retrieved_note.title == test_note.title
        assert retrieved_note.content == test_note.content

    async def test_get_note_by_id_not_found(self, db_session: AsyncSession, test_user):
        """测试获取不存在的笔记"""
        repo = NoteRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.get_by_id(9999, test_user)

    async def test_get_note_by_id_wrong_user(self, db_session: AsyncSession, test_user, another_user, test_note):
        """测试获取不属于当前用户的笔记"""
        repo = NoteRepository(db_session)
        
        # 另一个用户尝试获取笔记应该失败
        with pytest.raises(NotFoundException):
            await repo.get_by_id(test_note.id, another_user)

    async def test_get_all_notes_empty(self, db_session: AsyncSession, test_user):
        """测试获取空笔记列表"""
        repo = NoteRepository(db_session)
        
        notes = await repo.get_all(search=None, order_by=None, limit=10, offset=0, current_user=test_user)
        
        assert len(notes) == 0

    async def test_get_all_notes_with_data(self, db_session: AsyncSession, test_user, multiple_test_notes):
        """测试获取所有笔记"""
        repo = NoteRepository(db_session)
        
        notes = await repo.get_all(search=None, order_by=None, limit=10, offset=0, current_user=test_user)
        
        assert len(notes) == len(multiple_test_notes)
        assert all(note.user_id == test_user.id for note in notes)

    async def test_get_all_notes_with_search(self, db_session: AsyncSession, test_user):
        """测试带搜索条件的获取笔记"""
        repo = NoteRepository(db_session)
        
        # 创建测试数据
        note1 = Note(title="Python", content="Learning Python", user_id=test_user.id)
        note2 = Note(title="SQL", content="Database SQL", user_id=test_user.id)
        db_session.add_all([note1, note2])
        await db_session.commit()
        
        # 搜索标题
        notes = await repo.get_all(search="Python", order_by=None, limit=10, offset=0, current_user=test_user)
        assert len(notes) == 1
        assert notes[0].title == "Python"
        
        # 搜索内容
        notes = await repo.get_all(search="Database", order_by=None, limit=10, offset=0, current_user=test_user)
        assert len(notes) == 1
        assert notes[0].title == "SQL"

    async def test_get_all_notes_with_ordering(self, db_session: AsyncSession, test_user):
        """测试带排序的获取笔记"""
        repo = NoteRepository(db_session)
        
        # 创建测试数据
        note1 = Note(title="A", content="1", user_id=test_user.id)
        note2 = Note(title="B", content="2", user_id=test_user.id)
        db_session.add_all([note1, note2])
        await db_session.commit()
        
        # 升序排序
        notes_asc = await repo.get_all(search=None, order_by="created_at asc", limit=10, offset=0, current_user=test_user)
        assert notes_asc[0].title == "A"
        assert notes_asc[1].title == "B"
        
        # 降序排序
        notes_desc = await repo.get_all(search=None, order_by="created_at desc", limit=10, offset=0, current_user=test_user)
        assert notes_desc[0].title == "B"
        assert notes_desc[1].title == "A"

    async def test_get_all_notes_pagination(self, db_session: AsyncSession, test_user):
        """测试分页功能"""
        repo = NoteRepository(db_session)
        
        # 创建20条测试数据
        notes = [
            Note(title=f"Note {i}", content=f"Content {i}", user_id=test_user.id)
            for i in range(20)
        ]
        db_session.add_all(notes)
        await db_session.commit()
        
        # 第一页
        page1 = await repo.get_all(search=None, order_by=None, limit=10, offset=0, current_user=test_user)
        assert len(page1) == 10
        
        # 第二页
        page2 = await repo.get_all(search=None, order_by=None, limit=10, offset=10, current_user=test_user)
        assert len(page2) == 10
        
        # 检查不重叠
        assert all(note.id not in {n.id for n in page2} for note in page1)

    async def test_update_note_success(self, db_session: AsyncSession, test_user, test_note):
        """测试成功更新笔记"""
        repo = NoteRepository(db_session)
        update_data = NoteUpdate(title="Updated Title", content="Updated content")
        
        updated_note = await repo.update(update_data, test_note.id, test_user)
        
        assert updated_note.id == test_note.id
        assert updated_note.title == "Updated Title"
        assert updated_note.content == "Updated content"
        assert updated_note.user_id == test_user.id

    async def test_update_note_partial(self, db_session: AsyncSession, test_user, test_note):
        """测试部分更新笔记"""
        repo = NoteRepository(db_session)
        original_title = test_note.title
        update_data = NoteUpdate(content="Only update content")
        
        updated_note = await repo.update(update_data, test_note.id, test_user)
        
        assert updated_note.id == test_note.id
        assert updated_note.title == original_title  # 标题未改变
        assert updated_note.content == "Only update content"

    async def test_update_note_not_found(self, db_session: AsyncSession, test_user):
        """测试更新不存在的笔记"""
        repo = NoteRepository(db_session)
        update_data = NoteUpdate(title="Updated Title", content="Updated content")
        
        with pytest.raises(NotFoundException):
            await repo.update(update_data, 9999, test_user)

    async def test_update_note_no_fields(self, db_session: AsyncSession, test_user, test_note):
        """测试没有提供更新字段的情况"""
        repo = NoteRepository(db_session)
        update_data = NoteUpdate()
        
        with pytest.raises(ValueError, match="No fields to update"):
            await repo.update(update_data, test_note.id, test_user)

    async def test_delete_note_success(self, db_session: AsyncSession, test_user, test_note):
        """测试成功删除笔记"""
        repo = NoteRepository(db_session)
        
        await repo.delete(test_note.id, test_user)
        
        # 验证笔记已被删除
        with pytest.raises(NotFoundException):
            await repo.get_by_id(test_note.id, test_user)

    async def test_delete_note_not_found(self, db_session: AsyncSession, test_user):
        """测试删除不存在的笔记"""
        repo = NoteRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.delete(9999, test_user)

    async def test_delete_note_wrong_user(self, db_session: AsyncSession, test_user, another_user, test_note):
        """测试删除不属于当前用户的笔记"""
        repo = NoteRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.delete(test_note.id, another_user)