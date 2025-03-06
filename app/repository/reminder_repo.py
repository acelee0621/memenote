from sqlalchemy import select, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.models import Reminder
from app.schemas.schemas import ReminderCreate, ReminderUpdate


class ReminderRepository:
    def __init__(self, session: AsyncSession):
        """Repository layer for reminder operations."""
        self.session = session

    async def create(
        self, data: ReminderCreate, note_id: int | None, current_user
    ) -> Reminder:
        """
        Asynchronously creates a new reminder in the database.
        Args:
            data (ReminderCreate): The data required to create a new reminder.
            note_id (int | None): The ID of the note associated with the reminder, if any.
            current_user: The current user creating the reminder.
        Returns:
            Reminder: The newly created reminder object.
        Raises:
            Exception: If the database operation fails.
        """
        new_reminder = Reminder(
            reminder_time=data.reminder_time,
            message=data.message,
            note_id=note_id,
            user_id=current_user.id,
        )
        self.session.add(new_reminder)
        try:
            await self.session.commit()
            await self.session.refresh(new_reminder)
            return new_reminder
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Database operation failed, create failed {e}")

    async def get_by_id(self, reminder_id: int, current_user) -> Reminder:
        """
        Retrieve a reminder by its ID for the current user.
        Args:
            reminder_id (int): The ID of the reminder to retrieve.
            current_user: The current user object containing user details.
        Returns:
            Reminder: The reminder object if found.
        Raises:
            NotFoundException: If no reminder with the given ID is found for the current user.
        """
        query = select(Reminder).where(
            Reminder.id == reminder_id, Reminder.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        reminder = result.one_or_none()
        if not reminder:
            raise NotFoundException(f"Reminder with id {reminder_id} not found")
        return reminder

    async def get_all(
        self,
        note_id: int | None,
        search: str | None,
        order_by: str | None,
        current_user,
    ) -> list[Reminder]:
        """
        Retrieve all reminders for the current user.
        Args:
            current_user: The user whose reminders are to be retrieved.
        Returns:
            A list of Reminder objects associated with the current user.
        """
        query = select(Reminder).where(Reminder.user_id == current_user.id)

        if note_id:
            query = query.where(Reminder.note_id == note_id)

        if search:
            query = query.where(Reminder.message.ilike(f"%{search}%"))

        if order_by:
            if order_by == "created_at desc":
                query = query.order_by(desc(Reminder.created_at))
            elif order_by == "created_at asc":
                query = query.order_by(asc(Reminder.created_at))

        result = await self.session.scalars(query)
        return list(result.all())

    async def update(
        self, data: ReminderUpdate, reminder_id: int, current_user
    ) -> Reminder:
        """
        Updates an existing reminder with the provided data.
        Args:
            data (ReminderUpdate): The data to update the reminder with.
            reminder_id (int): The ID of the reminder to update.
            current_user: The current user performing the update.
        Returns:
            Reminder: The updated reminder object.
        Raises:
            NotFoundException: If the reminder with the given ID is not found or does not belong to the current user.
            ValueError: If there are no fields to update.
        """
        query = select(Reminder).where(
            Reminder.id == reminder_id, Reminder.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        reminder = result.one_or_none()
        if not reminder:
            raise NotFoundException(
                f"Reminder with id {reminder_id} not found or does not belong to the current user"
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        update_data.pop("id", None)
        update_data.pop("user_id", None)
        update_data.pop("note_id", None)
        if not update_data:
            raise ValueError("No fields to update")
        for key, value in update_data.items():
            setattr(reminder, key, value)
        await self.session.commit()
        await self.session.refresh(reminder)
        return reminder

    async def delete(self, reminder_id: int, current_user) -> None:
        """
        Deletes a reminder from the repository.
        Args:
            reminder_id (int): The ID of the reminder to delete.
            current_user: The user attempting to delete the reminder.
        Raises:
            NotFoundException: If the reminder does not exist or does not belong to the current user.
        """
        todo = await self.session.get(Reminder, reminder_id)
        if not todo or todo.user_id != current_user.id:
            raise NotFoundException(f"Reminder with id {reminder_id} not found")
        await self.session.delete(todo)
        await self.session.commit()
