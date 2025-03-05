from typing import Annotated

from fastapi import Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Note
from app.core.exceptions import NotFoundException


async def get_note_id(
    note_id: Annotated[
        int | None,
        Query(description="Add Item to a Note identified by the given ID."),
    ] = None,
    session: AsyncSession = Depends(get_db),
) -> int | None:
    """Get note_id as dependency."""
    if note_id is not None:
        note = await session.get(Note, note_id)
        if note is None:
            raise NotFoundException(f"Note with id {note_id} not found")
    return note_id
