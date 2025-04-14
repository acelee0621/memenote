import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import UniqueConstraint
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


# 基类
class Base(DeclarativeBase):
    pass


class DateTimeMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class User(SQLAlchemyBaseUserTable[int], DateTimeMixin, Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(100), index=True, unique=True, nullable=False
    )
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
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
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", back_populates="user", cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", back_populates="user", cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"



# 笔记表
class Note(Base, DateTimeMixin):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False, default="Untitled")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    share_code: Mapped[str] = mapped_column(
        String(36), index=True, nullable=True, unique=True, default=None
    )
    share_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    # 关系映射
    user: Mapped["User"] = relationship("User", back_populates="notes")
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="note", lazy="selectin"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        "Reminder", back_populates="note", lazy="selectin"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="note_tags", back_populates="notes", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "content", name="_user_content_unique_constraint"),
    )

    def generate_share_code(self):
        """生成唯一的 share_code"""
        self.share_code = str(uuid.uuid4())

    def __repr__(self):
        return f"<Note(id={self.id}, title={self.title})>"


# 待办事项表
class Todo(Base, DateTimeMixin):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
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
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    note_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("notes.id", ondelete="SET NULL"), nullable=True
    )
    reminder_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)

    # 关系映射
    user: Mapped["User"] = relationship("User", back_populates="reminders")
    note: Mapped[Optional["Note"]] = relationship("Note", back_populates="reminders")

    def __repr__(self):
        return f"<Reminder(id={self.id}, message={self.message})>"


class Attachment(Base, DateTimeMixin):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    object_name: Mapped[str] = mapped_column(
        String(512), nullable=False, unique=True, index=True
    )
    bucket_name: Mapped[str] = mapped_column(String(100), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # 使用 BigInteger 以支持大于 2GB 的文件
    # 关系映射 (反向)
    note: Mapped["Note"] = relationship("Note", back_populates="attachments")
    user: Mapped["User"] = relationship("User", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.original_filename}', object_name='{self.object_name}')>"


class Tag(Base, DateTimeMixin):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notes: Mapped[list["Note"]] = relationship(
        "Note", secondary="note_tags", back_populates="tags", lazy="selectin"
    )
    user: Mapped["User"] = relationship("User", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="_user_tag_name_unique_constraint"),
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name})>"


class NoteTag(Base):
    __tablename__ = "note_tags"

    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )
