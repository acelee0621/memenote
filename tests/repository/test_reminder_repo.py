import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.models import Reminder
from app.repository.reminder_repo import ReminderRepository
from app.schemas.schemas import ReminderCreate, ReminderUpdate


@pytest.mark.asyncio
class TestReminderRepository:
    async def test_create_reminder_success(self, db_session: AsyncSession, test_user):
        """测试成功创建提醒"""
        repo = ReminderRepository(db_session)
        reminder_time = datetime.now() + timedelta(days=1)
        reminder_data = ReminderCreate(
            reminder_time=reminder_time,
            message="Test reminder message"
        )
        
        created_reminder = await repo.create(reminder_data, None, test_user)
        
        assert created_reminder.id is not None
        assert created_reminder.message == "Test reminder message"
        assert created_reminder.user_id == test_user.id
        assert created_reminder.note_id is None
        assert created_reminder.reminder_time == reminder_time

    async def test_create_reminder_with_note(self, db_session: AsyncSession, test_user, test_note):
        """测试创建关联到Note的提醒"""
        repo = ReminderRepository(db_session)
        reminder_time = datetime.now() + timedelta(days=1)
        reminder_data = ReminderCreate(
            reminder_time=reminder_time,
            message="Reminder with note"
        )
        
        created_reminder = await repo.create(reminder_data, test_note.id, test_user)
        
        assert created_reminder.note_id == test_note.id

    async def test_get_reminder_by_id_success(self, db_session: AsyncSession, test_user, test_reminder):
        """测试通过ID获取提醒"""
        repo = ReminderRepository(db_session)
        
        retrieved_reminder = await repo.get_by_id(test_reminder.id, test_user)
        
        assert retrieved_reminder.id == test_reminder.id
        assert retrieved_reminder.message == test_reminder.message

    async def test_get_reminder_by_id_not_found(self, db_session: AsyncSession, test_user):
        """测试获取不存在的提醒"""
        repo = ReminderRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.get_by_id(9999, test_user)

    async def test_get_reminder_by_id_wrong_user(self, db_session: AsyncSession, test_user, another_user, test_reminder):
        """测试获取不属于当前用户的提醒"""
        repo = ReminderRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.get_by_id(test_reminder.id, another_user)

    async def test_get_all_reminders_empty(self, db_session: AsyncSession, test_user):
        """测试获取空提醒列表"""
        repo = ReminderRepository(db_session)
        
        reminders = await repo.get_all(None, None, None, test_user)
        
        assert len(reminders) == 0

    async def test_get_all_reminders_with_data(self, db_session: AsyncSession, test_user, multiple_test_reminders):
        """测试获取所有提醒"""
        repo = ReminderRepository(db_session)
        
        reminders = await repo.get_all(None, None, None, test_user)
        
        assert len(reminders) == len(multiple_test_reminders)
        assert all(reminder.user_id == test_user.id for reminder in reminders)

    async def test_get_all_reminders_with_note_filter(self, db_session: AsyncSession, test_user, test_note):
        """测试按Note ID过滤提醒"""
        repo = ReminderRepository(db_session)
        
        # 创建3个提醒，其中2个关联到test_note
        reminder_time = datetime.now() + timedelta(days=1)
        reminder1 = Reminder(
            message="Reminder 1", 
            user_id=test_user.id, 
            note_id=test_note.id,
            reminder_time=reminder_time
        )
        reminder2 = Reminder(
            message="Reminder 2", 
            user_id=test_user.id, 
            note_id=test_note.id,
            reminder_time=reminder_time
        )
        reminder3 = Reminder(
            message="Reminder 3", 
            user_id=test_user.id,
            reminder_time=reminder_time
        )
        db_session.add_all([reminder1, reminder2, reminder3])
        await db_session.commit()
        
        # 查询关联到note的reminders
        reminders = await repo.get_all(test_note.id, None, None, test_user)
        assert len(reminders) == 2
        assert all(reminder.note_id == test_note.id for reminder in reminders)

    async def test_get_all_reminders_with_search(self, db_session: AsyncSession, test_user):
        """测试搜索提醒内容"""
        repo = ReminderRepository(db_session)
        reminder_time = datetime.now() + timedelta(days=1)
        
        # 创建测试数据
        reminder1 = Reminder(
            message="Buy milk", 
            user_id=test_user.id,
            reminder_time=reminder_time
        )
        reminder2 = Reminder(
            message="Read book", 
            user_id=test_user.id,
            reminder_time=reminder_time
        )
        db_session.add_all([reminder1, reminder2])
        await db_session.commit()
        
        # 搜索
        results = await repo.get_all(None, "milk", None, test_user)
        assert len(results) == 1
        assert "milk" in results[0].message.lower()

    async def test_get_all_reminders_with_ordering(self, db_session: AsyncSession, test_user):
        """测试提醒排序"""
        repo = ReminderRepository(db_session)
        base_time = datetime.now()
        
        # 创建测试数据
        reminder1 = Reminder(
            message="A", 
            user_id=test_user.id,
            reminder_time=base_time + timedelta(minutes=10)
        )
        reminder2 = Reminder(
            message="B", 
            user_id=test_user.id,
            reminder_time=base_time + timedelta(minutes=20)
        )
        db_session.add_all([reminder1, reminder2])
        await db_session.commit()
        
        # 升序
        asc_reminders = await repo.get_all(None, None, "created_at asc", test_user)
        assert asc_reminders[0].message == "A"
        
        # 降序
        desc_reminders = await repo.get_all(None, None, "created_at desc", test_user)
        assert desc_reminders[0].message == "B"

    async def test_update_reminder_success(self, db_session: AsyncSession, test_user, test_reminder):
        """测试成功更新提醒"""
        repo = ReminderRepository(db_session)
        new_time = datetime.now() + timedelta(days=2)
        update_data = ReminderUpdate(
            message="Updated message",
            reminder_time=new_time
        )
        
        updated_reminder = await repo.update(update_data, test_reminder.id, test_user)
        
        assert updated_reminder.message == "Updated message"
        assert updated_reminder.reminder_time == new_time

    async def test_update_reminder_partial(self, db_session: AsyncSession, test_user, test_reminder):
        """测试部分更新提醒"""
        repo = ReminderRepository(db_session)
        original_message = test_reminder.message
        new_time = datetime.now() + timedelta(days=2)
        update_data = ReminderUpdate(reminder_time=new_time)
        
        updated_reminder = await repo.update(update_data, test_reminder.id, test_user)
        
        assert updated_reminder.message == original_message  # 消息未改变
        assert updated_reminder.reminder_time == new_time  # 仅更新时间

    async def test_update_reminder_not_found(self, db_session: AsyncSession, test_user):
        """测试更新不存在的提醒"""
        repo = ReminderRepository(db_session)
        update_data = ReminderUpdate(message="Updated")
        
        with pytest.raises(NotFoundException):
            await repo.update(update_data, 9999, test_user)

    async def test_update_reminder_no_fields(self, db_session: AsyncSession, test_user, test_reminder):
        """测试没有提供更新字段的情况"""
        repo = ReminderRepository(db_session)
        update_data = ReminderUpdate()
        
        with pytest.raises(ValueError, match="No fields to update"):
            await repo.update(update_data, test_reminder.id, test_user)

    async def test_delete_reminder_success(self, db_session: AsyncSession, test_user, test_reminder):
        """测试成功删除提醒"""
        repo = ReminderRepository(db_session)
        
        await repo.delete(test_reminder.id, test_user)
        
        # 验证提醒已被删除
        with pytest.raises(NotFoundException):
            await repo.get_by_id(test_reminder.id, test_user)

    async def test_delete_reminder_not_found(self, db_session: AsyncSession, test_user):
        """测试删除不存在的提醒"""
        repo = ReminderRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.delete(9999, test_user)

    async def test_delete_reminder_wrong_user(self, db_session: AsyncSession, test_user, another_user, test_reminder):
        """测试删除不属于当前用户的提醒"""
        repo = ReminderRepository(db_session)
        
        with pytest.raises(NotFoundException):
            await repo.delete(test_reminder.id, another_user)