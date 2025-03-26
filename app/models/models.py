from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


# 基类
class Base(DeclarativeBase):
    pass


class DateTimeMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, index=True, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# 用户表
class User(Base, DateTimeMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(100), index=True, unique=True, nullable=False
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)

    # 关系映射
    notes: Mapped[list["Note"]] = relationship(
        "Note", back_populates="user", cascade="all, delete-orphan"
    )
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="user", cascade="all, delete-orphan"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


# 笔记表
class Note(Base, DateTimeMixin):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False, default="Untitled")
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 关系映射
    user: Mapped["User"] = relationship("User", back_populates="notes")
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="note", lazy="selectin"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="note", lazy="selectin"
    )
    
    __table_args__ = (
        UniqueConstraint('user_id', 'content', name='_user_content_unique_constraint'),
    )

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title})>"


# 待办事项表
class Todo(Base, DateTimeMixin):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    note_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("notes.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # 关系映射
    user: Mapped["User"] = relationship("User", back_populates="todos")
    note: Mapped[Optional["Note"]] = relationship("Note", back_populates="todos")

    def __repr__(self):
        return f"<Todo(id={self.id}, content={self.content})>"


# 提醒表
class Reminder(Base, DateTimeMixin):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    note_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("notes.id", ondelete="SET NULL"), nullable=True
    )
    reminder_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)

    # 关系映射
    user: Mapped["User"] = relationship("User", back_populates="reminders")
    note: Mapped[Optional["Note"]] = relationship("Note", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder(id={self.id}, message={self.message})>"
