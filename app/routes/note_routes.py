from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.logging import get_logger
from app.core.security import get_current_user
from app.core.dependencies import get_note_service
from app.service.note_service import NoteService
from app.schemas.schemas import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    UserResponse,
)
from app.schemas.param_schemas import NoteQueryParams
from app.routes import attachment_routes


# Set up logger for this module
logger = get_logger(__name__)


router = APIRouter(
    prefix="/notes", tags=["Notes"], dependencies=[Depends(get_current_user)]
)


router.include_router(
    attachment_routes.router,
    prefix="/{note_id}/attachments",   
)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    data: NoteCreate,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
) -> NoteResponse:
    """Create new note."""
    try:
        created_note = await service.create_note(data=data, current_user=current_user)
        logger.info(f"Created note {created_note.id}")
        return created_note
    except Exception as e:
        logger.error(f"Failed to create note: {str(e)}")
        raise


@router.get("", response_model=list[NoteResponse])
async def get_all_notes(
    params: Annotated[NoteQueryParams, Query()],
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
) -> list[NoteResponse]:
    """Get all notes."""
    try:
        all_notes = await service.get_notes(
            search=params.search,
            order_by=params.order_by,
            limit=params.limit,
            offset=params.offset,
            current_user=current_user,
        )
        logger.info(f"Retrieved {len(all_notes)} notes")
        return all_notes
    except Exception as e:
        logger.error(f"Failed to fetch all notes: {str(e)}")
        raise


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
) -> NoteResponse:
    """Get note by id."""
    try:
        note = await service.get_note(note_id=note_id, current_user=current_user)
        logger.info(f"Retrieved note {note_id}")
        return note
    except Exception as e:
        logger.error(f"Failed to get note {note_id}: {str(e)}")
        raise


@router.patch("/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK)
async def update_note(
    data: NoteUpdate,
    note_id: int,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
) -> NoteResponse:
    """Update note."""
    try:
        updated_note = await service.update_note(
            data=data, note_id=note_id, current_user=current_user
        )
        logger.info(f"Updated note {note_id}")
        return updated_note
    except Exception as e:
        logger.error(f"Failed to update note {note_id}: {str(e)}")
        raise


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete note."""
    try:
        await service.delete_note(note_id=note_id, current_user=current_user)
        logger.info(f"Deleted note {note_id}")
    except Exception as e:
        logger.error(f"Failed to delete note {note_id}: {str(e)}")
        raise
