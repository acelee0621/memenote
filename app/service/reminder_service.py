from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from copy import deepcopy

from app.core.logging import get_logger
from app.repository.reminder_repo import ReminderRepository
from app.schemas.schemas import ReminderCreate, ReminderUpdate, ReminderResponse

# Set up logger for this module
logger = get_logger(__name__)

class ReminderService:
    def __init__(self, repository: ReminderRepository):
        """Service layer for reminder operations."""

        self.repository = repository

    async def create_reminder(
        self, data: ReminderCreate, note_id: int | None, timezone:str, current_user
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
        try:
            local_tz = ZoneInfo(timezone)
        except ZoneInfoNotFoundError:
            logger.error(f"Invalid timezone: {timezone}")
            raise ValueError(f"Invalid timezone: {timezone}")

        utc_tz = ZoneInfo("UTC")
        local_time = data.reminder_time.replace(tzinfo=local_tz)
        utc_time = local_time.astimezone(utc_tz)
                
        new_data = deepcopy(data)
        new_data.reminder_time = utc_time

        new_reminder = await self.repository.create(new_data, note_id, current_user)
        return ReminderResponse.model_validate(new_reminder)

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

    async def get_reminders(self, current_user) -> list[ReminderResponse]:
        """
        Retrieve all reminders for the current user.
        Args:
            current_user: The user for whom to retrieve reminders.
        Returns:
            A list of ReminderResponse objects representing the user's reminders.
        """
        reminders = await self.repository.get_all(current_user)
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
