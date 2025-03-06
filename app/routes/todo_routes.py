from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.core.dependencies import get_note_id
from app.repository.todo_repo import TodoRepository
from app.service.todo_service import TodoService
from app.schemas.schemas import TodoCreate, TodoUpdate, TodoResponse, UserResponse


# Set up logger for this module
logger = get_logger(__name__)


router = APIRouter(tags=["Todos"], dependencies=[Depends(get_current_user)])


def get_todo_service(session: AsyncSession = Depends(get_db)) -> TodoService:
    """Dependency for getting TodoService instance."""
    repository = TodoRepository(session)
    return TodoService(repository)


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    data: TodoCreate,
    note_id: Annotated[int | None, Depends(get_note_id)],
    service: TodoResponse = Depends(get_todo_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TodoResponse:
    """Create new todo."""
    try:
        created_todo = await service.create_todo(
            data=data, note_id=note_id, current_user=current_user
        )
        logger.info(f"Created todo {created_todo.id}")
        return created_todo
    except Exception as e:
        logger.error(f"Failed to create todo: {str(e)}")
        raise


@router.get("/todos", response_model=list[TodoResponse])
async def get_all_todos(
    note_id: Annotated[int | None, Query(description="Filter by Note ID")] = None,
    status: Annotated[
        Literal["finished", "unfinished"] | None,
        Query(
            description="Filter by status (unfinished/finished)",
        ),
    ] = None,
    search: Annotated[str | None, Query(description="Search todos by content")] = None,
    order_by: Annotated[
        Literal["created_at desc", "created_at asc"] | None,
        Query(description="Order by field (e.g., created_at desc/asc)"),
    ] = None,
    service: TodoResponse = Depends(get_todo_service),
    current_user: UserResponse = Depends(get_current_user),
) -> list[TodoResponse]:
    """Get all todos."""
    try:
        all_todos = await service.get_todos(
            note_id=note_id,
            status=status,
            search=search,
            order_by=order_by,
            current_user=current_user,
        )
        logger.info(f"Retrieved {len(all_todos)} todos")
        return all_todos
    except Exception as e:
        logger.error(f"Failed to fetch all todos: {str(e)}")
        raise


@router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: int,
    service: TodoResponse = Depends(get_todo_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TodoResponse:
    """Get todo by id."""
    try:
        todo = await service.get_todo(todo_id=todo_id, current_user=current_user)
        logger.info(f"Retrieved todo {todo_id}")
        return todo
    except Exception as e:
        logger.error(f"Failed to get todo {todo_id}: {str(e)}")
        raise


@router.patch(
    "/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK
)
async def update_todo(
    data: TodoUpdate,
    todo_id: int,
    service: TodoResponse = Depends(get_todo_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TodoResponse:
    """Update todo."""
    try:
        updated_todo = await service.update_todo(
            data=data, todo_id=todo_id, current_user=current_user
        )
        logger.info(f"Updated todo {todo_id}")
        return updated_todo
    except Exception as e:
        logger.error(f"Failed to update todo {todo_id}: {str(e)}")
        raise


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    service: TodoResponse = Depends(get_todo_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete todo."""
    try:
        await service.delete_todo(todo_id=todo_id, current_user=current_user)
        logger.info(f"Deleted todo {todo_id}")
    except Exception as e:
        logger.error(f"Failed to delete todo {todo_id}: {str(e)}")
        raise
