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
        DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
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
    # 新增：与 Attachment 的一对多关系 (直接关联，方便查询用户的所有附件)
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", back_populates="user", cascade="all, delete-orphan"
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
    # 新增：与 Attachment 的一对多关系
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        back_populates="note",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "content", name="_user_content_unique_constraint"),
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
    # 外键关联到 Note 表
    note_id: Mapped[int] = mapped_column(
        ForeignKey(
            "notes.id", ondelete="CASCADE"
        ),  # 如果笔记删除，数据库层面也删除此附件记录
        nullable=False,
        index=True,
    )
    # 外键直接关联到 User 表 (方便权限检查和查询)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # MinIO 相关信息
    object_name: Mapped[str] = mapped_column(
        String(512),  # 存储在 MinIO 中的对象 key/路径，长度可以给足一些
        nullable=False,
        unique=True,  # 确保每个 MinIO 对象只被引用一次
        index=True,  # 频繁用于查找，需要索引
    )
    bucket_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    # 文件元数据
    original_filename: Mapped[str] = mapped_column(
        String(255),  # 用户上传时的原始文件名
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String(100),  # 文件的 MIME 类型
        nullable=False,
    )
    size: Mapped[int] = mapped_column(
        Integer,  # 使用 BigInteger 以支持大于 2GB 的文件
        nullable=False,
    )
    # 关系映射 (反向)
    note: Mapped["Note"] = relationship("Note", back_populates="attachments")
    user: Mapped["User"] = relationship("User", back_populates="attachments")

    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.original_filename}', object_name='{self.object_name}')>"
