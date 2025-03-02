from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

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
    title: str
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

# 待办事项相关模型
class TodoCreate(BaseModel):
    content: str = Field(..., max_length=255)
    note_id: int | None = None
    
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
    note_id: int | None = None
    

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
    timezone: str
    message: str | None = None    
    is_acknowledged: bool | None = None
    
    
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    

class LoginData(BaseModel):
    username: str
    password: str