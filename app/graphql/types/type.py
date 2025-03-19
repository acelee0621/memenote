import strawberry

from datetime import datetime

# DateTime scalar 类型
DateTime = strawberry.scalar(
    datetime,
    description="ISO 8601 encoded datetime string",
    serialize=lambda v: v.isoformat(),
    parse_value=lambda v: datetime.fromisoformat(v)
)

# 用户类型
@strawberry.type
class User:
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    created_at: datetime
    updated_at: datetime
    
    # 关系字段
    notes: list["Note"]
    todos: list["Todo"]
    reminders: list["Reminder"]

# 笔记类型
@strawberry.type
class Note:
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    
    # 关系字段
    user: User
    todos: list["Todo"]
    reminders: list["Reminder"]

# 待办事项类型
@strawberry.type
class Todo:
    id: int
    user_id: int
    note_id: int | None = None
    content: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    
    # 关系字段
    user: User
    note: Note | None = None

# 提醒类型
@strawberry.type
class Reminder:
    id: int
    user_id: int
    note_id: int | None = None
    reminder_time: datetime
    message: str
    is_triggered: bool
    is_acknowledged: bool
    created_at: datetime
    updated_at: datetime
    
    # 关系字段
    user: User
    note: Note | None = None