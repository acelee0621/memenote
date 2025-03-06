from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.core.dependencies import get_note_id
from app.repository.reminder_repo import ReminderRepository
from app.service.reminder_service import ReminderService
from app.schemas.schemas import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    UserResponse,
)


# Set up logger for this module
logger = get_logger(__name__)


router = APIRouter(tags=["Reminders"], dependencies=[Depends(get_current_user)])


def get_reminder_service(session: AsyncSession = Depends(get_db)) -> ReminderService:
    """Dependency for getting ReminderService instance."""
    repository = ReminderRepository(session)
    return ReminderService(repository)


@router.post(
    "/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED
)
async def create_reminder(
    data: ReminderCreate,
    note_id: Annotated[int | None, Depends(get_note_id)],
    service: ReminderResponse = Depends(get_reminder_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ReminderResponse:
    """Create new reminder."""
    try:
        created_reminder = await service.create_reminder(
            data=data, note_id=note_id, current_user=current_user
        )
        logger.info(f"Created reminder {created_reminder.id}")
        return created_reminder
    except Exception as e:
        logger.error(f"Failed to create reminder: {str(e)}")
        raise


@router.get("/reminders", response_model=list[ReminderResponse])
async def get_all_reminders(
    note_id: Annotated[int | None, Query(description="Filter by Note ID")] = None,
    search: Annotated[
        str | None, Query(description="Search reminders by message")
    ] = None,
    order_by: Annotated[
        Literal["created_at desc", "created_at asc"] | None,
        Query(description="Order by field (e.g., created_at desc/asc)"),
    ] = None,
    service: ReminderResponse = Depends(get_reminder_service),
    current_user: UserResponse = Depends(get_current_user),
) -> list[ReminderResponse]:
    """Get all reminders."""
    try:
        all_reminders = await service.get_reminders(
            note_id=note_id, search=search, order_by=order_by, current_user=current_user
        )
        logger.info(f"Retrieved {len(all_reminders)} reminders")
        return all_reminders
    except Exception as e:
        logger.error(f"Failed to fetch all reminders: {str(e)}")
        raise


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    service: ReminderResponse = Depends(get_reminder_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ReminderResponse:
    """Get reminder by id."""
    try:
        reminder = await service.get_reminder(
            reminder_id=reminder_id, current_user=current_user
        )
        logger.info(f"Retrieved reminder {reminder_id}")
        return reminder
    except Exception as e:
        logger.error(f"Failed to get reminder {reminder_id}: {str(e)}")
        raise


@router.patch(
    "/reminders/{reminder_id}",
    response_model=ReminderResponse,
    status_code=status.HTTP_200_OK,
)
async def update_reminder(
    data: ReminderUpdate,
    reminder_id: int,
    service: ReminderResponse = Depends(get_reminder_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ReminderResponse:
    """Update reminder."""
    try:
        updated_reminder = await service.update_reminder(
            data=data, reminder_id=reminder_id, current_user=current_user
        )
        logger.info(f"Updated reminder {reminder_id}")
        return updated_reminder
    except Exception as e:
        logger.error(f"Failed to update reminder {reminder_id}: {str(e)}")
        raise


@router.delete("/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    service: ReminderResponse = Depends(get_reminder_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete reminder."""
    try:
        await service.delete_reminder(
            reminder_id=reminder_id, current_user=current_user
        )
        logger.info(f"Deleted reminder {reminder_id}")
    except Exception as e:
        logger.error(f"Failed to delete reminder {reminder_id}: {str(e)}")
        raise
