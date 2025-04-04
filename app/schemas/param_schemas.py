from typing import Annotated, Literal
from pydantic import BaseModel, Field


# 基类，包含所有路由共享的查询参数
class CommonQueryParams(BaseModel):
    search: Annotated[
        str | None, Field(default=None, description="Text search parameter.")
    ]
    order_by: Annotated[
        Literal["created_at desc", "created_at asc"] | None,
        Field(default=None, description="Order by field"),
    ]


class NoteQueryParams(CommonQueryParams):
    limit: Annotated[
        int,
        Field(default=20, ge=1, le=100, description="Number of notes per page"),
    ]  # 默认每页20条,可被覆盖
    offset: Annotated[int, Field(default=0, ge=0, description="Offset for pagination")]


class TodoQueryParams(CommonQueryParams):
    # note_id: Annotated[
    #     int | None, Field(default=None, description="Filter by Note's ID")
    # ]
    status: Annotated[
        Literal["finished", "unfinished"] | None,
        Field(
            default=None,
            description="Filter by status",
        ),
    ]


class ReminderQueryParams(CommonQueryParams):
    pass


class AttachmentQueryParams(BaseModel):
    limit: Annotated[
        int,
        Field(default=20, ge=1, le=100, description="Number of attachments per page"),
    ]  # 默认每页20条,可被覆盖
    offset: Annotated[int, Field(default=0, ge=0, description="Offset for pagination")]