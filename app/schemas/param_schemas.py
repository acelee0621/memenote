from typing import Annotated, Literal
from pydantic import BaseModel

from fastapi import Query


# 基类，包含所有路由共享的查询参数
class CommonQueryParams(BaseModel):
    search: Annotated[
        str | None, Query(description="Search notes by title or content etc.")
    ] = None
    order_by: Annotated[
        Literal["Created_at desc", "Created_at asc"] | None,
        Query(description="Order by field"),
    ] = None


class NoteQueryParams(CommonQueryParams):
    limit: Annotated[
        int,
        Query(default=20, ge=1, le=100, description="Number of notes per page"),
    ]  # 默认每页20条,可被覆盖
    offset: Annotated[int, Query(default=0, ge=0, description="Offset for pagination")]


class TodoQueryParams(CommonQueryParams):
    note_id: Annotated[
        int | None, Query(default=None, description="Filter by Note's ID")
    ]
    status: Annotated[
        Literal["Finished", "Unfinished"] | None,
        Query(
            default=None,
            description="Filter by status",
        ),
    ]


class ReminderQueryParams(CommonQueryParams):
    note_id: Annotated[
        int | None, Query(default=None, description="Filter by Note's ID")
    ]
