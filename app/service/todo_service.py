from app.repository.todo_repo import TodoRepository
from app.schemas.schemas import TodoCreate, TodoUpdate, TodoResponse


class TodoService:
    def __init__(self, repository: TodoRepository):
        """Service layer for todo operations."""

        self.repository = repository

    async def create_todo(
        self, data: TodoCreate, note_id: int | None, current_user
    ) -> TodoResponse:
        """
        Asynchronously creates a new todo item.
        Args:
            data (TodoCreate): The data required to create a new todo item.
            note_id (int | None): The ID of the note to which the todo item is associated,
                                  or None if not associated with any note.
            current_user: The current user creating the todo item.
        Returns:
            TodoResponse: The response model containing the details of the newly created todo item.
        """
        new_todo = await self.repository.create(data, note_id, current_user)
        return TodoResponse.model_validate(new_todo)

    async def get_todo(self, todo_id: int, current_user) -> TodoResponse:
        """
        Retrieve a todo item by its ID for the current user.
        Args:
            todo_id (int): The ID of the todo item to retrieve.
            current_user: The user requesting the todo item.
        Returns:
            TodoResponse: The response model containing the todo item details.
        """

        todo = await self.repository.get_by_id(todo_id, current_user)
        return TodoResponse.model_validate(todo)

    async def get_todos(
        self,
        note_id: int | None,
        status: str | None,
        search: str | None,
        order_by: str | None,
        current_user,
    ) -> list[TodoResponse]:
        """
        Asynchronously retrieves a list of todos for the current user.
        Args:
            current_user: The user for whom to retrieve the todos.
        Returns:
            list[TodoResponse]: A list of TodoResponse objects representing the todos.
        """
        todos = await self.repository.get_all(
            note_id=note_id,
            status=status,
            search=search,
            order_by=order_by,
            current_user=current_user,
        )
        return [TodoResponse.model_validate(todo) for todo in todos]

    async def update_todo(
        self, data: TodoUpdate, todo_id: int, current_user
    ) -> TodoResponse:
        """
        Asynchronously updates a todo item with the given data.
        Args:
            data (TodoUpdate): The data to update the todo item with.
            todo_id (int): The ID of the todo item to update.
            current_user: The current user performing the update.
        Returns:
            TodoResponse: The updated todo item validated against the TodoResponse model.
        """
        todo = await self.repository.update(data, todo_id, current_user)
        return TodoResponse.model_validate(todo)

    async def delete_todo(self, todo_id: int, current_user) -> None:
        await self.repository.delete(todo_id, current_user)
