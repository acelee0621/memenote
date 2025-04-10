from typing import Annotated

from fastapi import Query, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.user_manage import get_current_user
# from app.core.security import get_current_user
from app.schemas.schemas import UserResponse
from app.models.models import Note
from app.core.exceptions import NotFoundException, ForbiddenException



async def validate_note(note_id: int, session: AsyncSession, current_user: UserResponse) -> None:
    note = await session.get(Note, note_id)
    if note is None:
        raise NotFoundException(f"Note with id {note_id} not found")
    if note.user_id != current_user.id:
        raise ForbiddenException("You do not have permission to access this note")

async def get_note_id(
    note_id: Annotated[int | None, Query(description="Add Item to a Note identified by the given ID.")] = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> int | None:
    if note_id is not None:
        await validate_note(note_id, session, current_user)
    return note_id

async def get_attachment_note_id(
    note_id: Annotated[int, Path(description="The ID of the note containing the attachment")],
    session: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> int:
    await validate_note(note_id, session, current_user)
    return note_id