from pydantic import BaseModel, ConfigDict, Field, computed_field
from datetime import datetime

from fastapi_users import schemas

from app.core.config import settings


# 配置基类，启用 ORM 模式
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserRead(schemas.BaseUser[int]):
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=100)
    created_at: datetime
    updated_at: datetime


class UserResponse(UserRead):
    pass


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=100)


class UserUpdate(schemas.BaseUserUpdate):
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=100)


# 笔记相关模型
class NoteCreate(BaseModel):
    title: str = Field(..., max_length=100)
    content: str


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NoteResponse(BaseSchema):
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    share_code: str | None = None
    share_expires_at: datetime | None = None
    tags: list["TagResponseForNote"] | None = None
    todos: list["TodoResponse"] | None = None
    reminders: list["ReminderResponse"] | None = None
    attachments: list["AttachmentResponse"] | None = None

    @computed_field
    def share_url(self) -> str | None:
        if self.share_code:
            return f"{settings.BASE_URL}/public/notes/{self.share_code}"
        return None


# 待办事项相关模型
class TodoCreate(BaseModel):
    content: str = Field(..., max_length=255)


class TodoUpdate(BaseModel):
    content: str | None = None
    is_completed: bool | None = None


class TodoResponse(BaseSchema):
    id: int
    user_id: int
    note_id: int | None = None
    content: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime


# 提醒相关模型
class ReminderCreate(BaseModel):
    reminder_time: datetime
    message: str = Field(..., max_length=255)


class ReminderResponse(BaseSchema):
    id: int
    user_id: int
    note_id: int | None = None
    reminder_time: datetime
    message: str
    is_triggered: bool
    is_acknowledged: bool
    created_at: datetime


# 更新模型（可选字段）
class ReminderUpdate(BaseModel):
    reminder_time: datetime | None = None
    message: str | None = None
    is_acknowledged: bool | None = None


class AttachmentBase(BaseSchema):
    note_id: int = Field(..., description="关联的笔记ID")
    object_name: str = Field(..., max_length=512, description="MinIO对象存储路径")
    bucket_name: str = Field(..., max_length=100, description="MinIO存储桶名称")
    original_filename: str = Field(..., max_length=255, description="原始文件名")
    content_type: str = Field(..., max_length=100, description="文件MIME类型")
    size: int = Field(..., description="文件大小(字节)")


# 创建附件时的请求模型
class AttachmentCreate(AttachmentBase):
    pass


# 附件响应模型
class AttachmentResponse(AttachmentBase):
    id: int = Field(..., description="附件ID")
    user_id: int = Field(..., description="所属用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class PresignedUrlResponse(BaseModel):
    url: str = Field(..., description="Pre-signed URL for the attachment")
    expires_at: datetime = Field(
        ..., description="Expiration time of the pre-signed URL"
    )
    filename: str = Field(..., description="Original filename of the attachment")
    content_type: str = Field(..., description="MIME type of the attachment")
    size: int = Field(..., description="Size of the attachment in bytes")
    attachment_id: int = Field(..., description="ID of the attachment")


class TagCreate(BaseModel):
    name: str = Field(..., max_length=50)


class TagUpdate(BaseModel):
    name: str | None = None


class TagResponseForNote(BaseSchema):
    id: int
    name: str


class TagResponse(TagResponseForNote):
    user_id: int
    created_at: datetime
    updated_at: datetime
