from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.database import get_db
from app.repository.note_repo import NoteRepository
from app.service.note_service import NoteService
from app.schemas.schemas import NoteResponse

logger = get_logger(__name__)


public_router = APIRouter(prefix="/public", tags=["Public"])

def get_note_service(session: AsyncSession = Depends(get_db)) -> NoteService:
    return NoteService(NoteRepository(session))

@public_router.get("/notes/{share_code}", response_model=NoteResponse)
async def get_shared_note(
    share_code: str,
    service: NoteService = Depends(get_note_service),
):
    try:
        note = await service.get_note_by_share_code(share_code)
        logger.info(f"Retrieved shared note {share_code}")
        return note
    except Exception as e:
        logger.error(f"Failed to get shared note: {str(e)}")
        raise