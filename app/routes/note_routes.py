from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.database import get_db
from app.core.security import get_current_user
from app.repository.note_repo import NoteRepository
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

# Include attachment routes
router.include_router(attachment_routes.router)


def get_note_service(session: AsyncSession = Depends(get_db)) -> NoteService:
    """Dependency for getting NoteService instance."""
    repository = NoteRepository(session)
    return NoteService(repository)


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
            tag_id=params.tag_id,
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


@router.post(
    "/{note_id}/tags/{tag_id}",
    response_model=NoteResponse,
    status_code=status.HTTP_200_OK,
    summary="[Tags] Add a tag to a specific note",
)
async def add_tag_to_note(
    note_id: int,
    tag_id: int,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
) -> NoteResponse:
    try:
        updated_note = await service.add_tag_to_note(note_id, tag_id, current_user)
        logger.info(f"Added tag {tag_id} to note {note_id} for user {current_user.id}")
        return updated_note
    except Exception as e:
        logger.error(f"Failed to add tag {tag_id} to note {note_id}: {str(e)}")
        raise


@router.delete(
    "/{note_id}/tags/{tag_id}",
    response_model=NoteResponse,
    status_code=status.HTTP_200_OK,
    summary="[Tags] Remove a tag to a specific note",
)
async def remove_tag_from_note(
    note_id: int,
    tag_id: int,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
) -> NoteResponse:
    try:
        updated_note = await service.remove_tag_from_note(note_id, tag_id, current_user)
        logger.info(
            f"Removed tag {tag_id} from note {note_id} for user {current_user.id}"
        )
        return updated_note
    except Exception as e:
        logger.error(f"Failed to remove tag {tag_id} from note {note_id}: {str(e)}")
        raise


@router.post(
    "/{note_id}/share",
    response_model=NoteResponse,
    dependencies=[Depends(get_current_user)],
)
async def enable_share(
    note_id: int,
    expires_in: Annotated[
        int,
        Query(            
            description="Expiration time in seconds (default: 7 days)",            
            ge=60,
            le=2592000,
        ),
    ] = 604800,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        updated_note = await service.enable_share(note_id, expires_in, current_user)
        logger.info(
            f"Enabled sharing for note {note_id} with share_code {updated_note.share_code}"
        )
        return updated_note
    except Exception as e:
        logger.error(f"Failed to enable sharing for note {note_id}: {str(e)}")
        raise


@router.delete(
    "/{note_id}/share",
    response_model=NoteResponse,
    dependencies=[Depends(get_current_user)],
)
async def disable_share(
    note_id: int,
    service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        updated_note = await service.disable_share(note_id, current_user)
        logger.info(f"Disabled sharing for note {note_id}")
        return updated_note
    except Exception as e:
        logger.error(f"Failed to disable sharing for note {note_id}: {str(e)}")
        raise
