from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from sqlalchemy import inspect

from app.models.models import Attachment

# 配置基类，启用 ORM 模式
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# 用户相关模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr | None = Field(None, max_length=255)
    full_name: str | None = Field(None, max_length=100)
    password: str = Field(..., min_length=3)
    
    
class UserInDB(BaseSchema):
    id: int
    username: str
    email: EmailStr | None = None
    full_name: str | None = None
    password_hash: str
    

class UserResponse(BaseSchema):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime

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
    todos: list["TodoResponse"] | None = None
    reminders: list["ReminderResponse"] | None = None
    attachments: list["AttachmentResponse"] | None = None

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
    message: str = Field(...,max_length=255)    

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
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    

class LoginData(BaseModel):
    username: str
    password: str
    
    
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

# 更新附件时的请求模型（所有字段可选）
class AttachmentUpdate(BaseModel):
    note_id: int | None = Field(None, description="关联的笔记ID")
    original_filename: str | None = Field(None, max_length=255, description="原始文件名")
    content_type: str | None = Field(None, max_length=100, description="文件MIME类型")

# 附件响应模型
class AttachmentResponse(AttachmentBase):
    id: int = Field(..., description="附件ID")
    user_id: int = Field(..., description="所属用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    