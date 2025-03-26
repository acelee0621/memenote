from datetime import datetime, timedelta

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, Note, Todo, Reminder



@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """创建一个测试用户"""
    user = User(username="testuser", email="test@example.com", password_hash="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def another_user(db_session: AsyncSession):
    """创建另一个测试用户"""
    user = User(username="anotheruser", email="another@example.com", password_hash="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def test_note(db_session: AsyncSession, test_user):
    """创建一个测试笔记"""
    note = Note(title="Test Note", content="Test Content", user_id=test_user.id)
    db_session.add(note)
    await db_session.commit()
    await db_session.refresh(note)
    return note

@pytest_asyncio.fixture
async def multiple_test_notes(db_session: AsyncSession, test_user):
    """创建多个测试笔记"""
    notes = [
        Note(title=f"Note {i}", content=f"Content {i}", user_id=test_user.id)
        for i in range(5)
    ]
    db_session.add_all(notes)
    await db_session.commit()
    return notes


@pytest_asyncio.fixture
async def test_todo(db_session: AsyncSession, test_user):
    """创建一个测试Todo"""
    todo = Todo(content="Test Todo", user_id=test_user.id)
    db_session.add(todo)
    await db_session.commit()
    await db_session.refresh(todo)
    return todo

@pytest_asyncio.fixture
async def multiple_test_todos(db_session: AsyncSession, test_user):
    """创建多个测试Todo"""
    todos = [
        Todo(content=f"Todo {i}", user_id=test_user.id)
        for i in range(5)
    ]
    db_session.add_all(todos)
    await db_session.commit()
    return todos


@pytest_asyncio.fixture
async def test_reminder(db_session: AsyncSession, test_user):
    """创建一个测试提醒"""
    reminder_time = datetime.now() + timedelta(days=1)
    reminder = Reminder(
        message="Test Reminder",
        reminder_time=reminder_time,
        user_id=test_user.id
    )
    db_session.add(reminder)
    await db_session.commit()
    await db_session.refresh(reminder)
    return reminder

@pytest_asyncio.fixture
async def multiple_test_reminders(db_session: AsyncSession, test_user):
    """创建多个测试提醒"""
    base_time = datetime.now()
    reminders = [
        Reminder(
            message=f"Reminder {i}",
            reminder_time=base_time + timedelta(hours=i),
            user_id=test_user.id
        )
        for i in range(5)
    ]
    db_session.add_all(reminders)
    await db_session.commit()
    return reminders