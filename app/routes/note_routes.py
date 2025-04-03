from typing import Annotated
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.repository.note_repo import NoteRepository
from app.service.note_service import NoteService
from app.repository.attachment_repo import AttachmentRepository
from app.service.attachment_service import AttachmentService
from app.schemas.schemas import NoteCreate, NoteUpdate, NoteResponse, UserResponse, AttachmentResponse
from app.schemas.param_schemas import NoteQueryParams


# Set up logger for this module
logger = get_logger(__name__)


router = APIRouter(tags=["Notes"], dependencies=[Depends(get_current_user)])


def get_note_service(session: AsyncSession = Depends(get_db)) -> NoteService:
    """Dependency for getting NoteService instance."""
    repository = NoteRepository(session)
    return NoteService(repository)

def get_attachment_service(session: AsyncSession = Depends(get_db)) -> AttachmentService:
    """Dependency for getting NoteService instance."""
    repository = AttachmentRepository(session)
    return AttachmentService(repository)


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("/notes", response_model=list[NoteResponse])
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


@router.get("/notes/{note_id}", response_model=NoteResponse)
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


@router.patch(
    "/notes/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK
)
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


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    "/notes/{note_id}/attachments",
    response_model=AttachmentResponse, # 返回新创建的附件信息
    status_code=status.HTTP_201_CREATED,
    summary="Upload an attachment for a specific note" # 添加 OpenAPI 描述
)
async def upload_note_attachment(
    note_id: int,
    file: UploadFile = File(...), # 使用 FastAPI 的 UploadFile 来接收文件    
    attachment_service: AttachmentService = Depends(get_attachment_service),    
    note_service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),    
):
    
    try:
        # 1. 验证 Note 是否存在且属于当前用户
        note = await note_service.get_note(note_id=note_id, current_user=current_user)
        if not note:             
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or insufficient permissions")

        # 2. 上传附件        
        created_attachment = await attachment_service.add_attachment_to_note(
            file=file,
            note_id=note_id,
            current_user=current_user                         
        )
        logger.info(f"Uploaded attachment {created_attachment.id} for note {note_id}")
        return created_attachment # 返回创建的附件信息

    except HTTPException as http_exc:
        raise http_exc # 重新抛出已知的 HTTP 异常
    except Exception as e:
        logger.error(f"Failed to upload attachment for note {note_id}: {str(e)}")
        # 在生产环境中，避免暴露详细错误
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload attachment")
