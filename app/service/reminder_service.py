from app.repository.reminder_repo import ReminderRepository
from app.schemas.schemas import ReminderCreate, ReminderUpdate, ReminderResponse
from app.core.celery_app import celery_app


class ReminderService:
    def __init__(self, repository: ReminderRepository):
        """Service layer for reminder operations."""

        self.repository = repository

    async def create_reminder(
        self, data: ReminderCreate, note_id: int | None, current_user
    ) -> ReminderResponse:
        """
        Asynchronously creates a new reminder.
        Args:
            data (ReminderCreate): The data required to create a new reminder.
            note_id (int | None): The ID of the note associated with the reminder,
                                  or None if not applicable.
            current_user: The current user creating the reminder.
        Returns:
            ReminderResponse: The response model containing the details of the created reminder.
        """
        new_reminder = await self.repository.create(data, note_id, current_user)
        result = ReminderResponse.model_validate(new_reminder)
        
        # 触发 Celery 任务通知 WebSocket
        celery_app.send_task(
        "app.tasks.reminder.notify_reminder_creation",
        args=[{
            "reminder_id": result.id,
            "reminder_time": result.reminder_time,
            "message": result.message,
            "user_id": result.user_id,
            "note_id": result.note_id
        }])
        
        
        return result

    async def get_reminder(self, reminder_id: int, current_user) -> ReminderResponse:
        """
        Retrieve a reminder by its ID for the current user.
        Args:
            reminder_id (int): The ID of the reminder to retrieve.
            current_user: The user requesting the reminder.
        Returns:
            ReminderResponse: The response model containing the reminder details.
        """
        reminder = await self.repository.get_by_id(reminder_id, current_user)
        return ReminderResponse.model_validate(reminder)

    async def get_reminders(
        self,
        note_id: int | None,
        search: str | None,
        order_by: str | None,
        current_user,
    ) -> list[ReminderResponse]:
        """
        Retrieve all reminders for the current user.
        Args:
            current_user: The user for whom to retrieve reminders.
        Returns:
            A list of ReminderResponse objects representing the user's reminders.
        """
        reminders = await self.repository.get_all(
            note_id=note_id, search=search, order_by=order_by, current_user=current_user
        )
        return [ReminderResponse.model_validate(reminder) for reminder in reminders]

    async def update_reminder(
        self, data: ReminderUpdate, reminder_id: int, current_user
    ) -> ReminderResponse:
        """
        Asynchronously updates a reminder with the given data.
        Args:
            data (ReminderUpdate): The data to update the reminder with.
            reminder_id (int): The ID of the reminder to update.
            current_user: The current user performing the update.
        Returns:
            ReminderResponse: The updated reminder response.
        """
        reminder = await self.repository.update(data, reminder_id, current_user)
        return ReminderResponse.model_validate(reminder)

    async def delete_reminder(self, reminder_id: int, current_user) -> None:
        """
        Deletes a reminder for the current user.
        Args:
            reminder_id (int): The ID of the reminder to be deleted.
            current_user: The user who owns the reminder.
        Returns:
            None
        """
        await self.repository.delete(reminder_id, current_user)
