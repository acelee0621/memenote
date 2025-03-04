from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.models import Todo
from app.schemas.schemas import TodoCreate, TodoUpdate


class TodoRepository:
    def __init__(self, session: AsyncSession):
        """Repository layer for todo operations."""
        self.session = session

    async def create(self, data: TodoCreate, note_id: int | None, current_user) -> Todo:
        """
        Create a new Todo item.
        Args:
            data (TodoCreate): The data required to create a new Todo item.
            note_id (int | None): The ID of the associated note, if any.
            current_user: The current user creating the Todo item.
        Returns:
            Todo: The newly created Todo item.
        Raises:
            Exception: If the database operation fails.
        """
        new_todo = Todo(content=data.content, note_id=note_id, user_id=current_user.id)
        self.session.add(new_todo)
        try:
            await self.session.commit()
            await self.session.refresh(new_todo)
            return new_todo
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Database operation failed, create failed {e}")

    async def get_by_id(self, todo_id: int, current_user) -> Todo:
        """
        Retrieve a Todo item by its ID for the current user.
        Args:
            todo_id (int): The ID of the Todo item to retrieve.
            current_user: The current user object containing user details.
        Returns:
            Todo: The Todo item if found.
        Raises:
            NotFoundException: If no Todo item with the given ID is found for the current user.
        """
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
        result = await self.session.scalars(query)
        todo = result.one_or_none()
        if not todo:
            raise NotFoundException(f"Todo with id {todo_id} not found")
        return todo

    async def get_all(self, current_user) -> list[Todo]:
        """
        Retrieve all Todo items for the current user.
        Args:
            current_user: The user whose Todo items are to be retrieved.
        Returns:
            A list of Todo items associated with the current user.
        """
        result = await self.session.scalars(
            select(Todo).where(Todo.user_id == current_user.id)
        )
        return result.all()

    async def update(self, data: TodoUpdate, todo_id: int, current_user) -> Todo:
        """
        Update a Todo item with the given data.
        Args:
            data (TodoUpdate): The data to update the Todo item with.
            todo_id (int): The ID of the Todo item to update.
            current_user: The current user performing the update.
        Returns:
            Todo: The updated Todo item.
        Raises:
            NotFoundException: If the Todo item with the given ID is not found or does not belong to the current user.
            ValueError: If there are no fields to update.
        """
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
        result = await self.session.scalars(query)
        todo = result.one_or_none()
        if not todo:
            raise NotFoundException(
                f"Todo with id {todo_id} not found or does not belong to the current user"
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("id", None)
        update_data.pop("user_id", None)
        update_data.pop("note_id", None)
        if not update_data:
            raise ValueError("No fields to update")
        for key, value in update_data.items():
            setattr(todo, key, value)
        await self.session.commit()
        await self.session.refresh(todo)
        return todo

    async def delete(self, todo_id: int, current_user) -> None:
        """
        Deletes a todo item from the database.
        Args:
            todo_id (int): The ID of the todo item to delete.
            current_user: The current authenticated user.
        Raises:
            NotFoundException: If the todo item is not found or does not belong to the current user.
        """
        todo = await self.session.get(Todo, todo_id)

        if not todo or todo.user_id != current_user.id:
            raise NotFoundException(f"Todo with id {todo_id} not found")

        await self.session.delete(todo)
        await self.session.commit()
