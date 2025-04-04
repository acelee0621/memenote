from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.core.dependencies import get_note_service
from app.service.note_service import NoteService
from app.service.attachment_service import AttachmentService
from app.repository.attachment_repo import AttachmentRepository
from app.schemas.schemas import UserResponse, AttachmentResponse


logger = get_logger(__name__)


router = APIRouter()


def get_attachment_service(
    session: AsyncSession = Depends(get_db),
) -> AttachmentService:
    """Dependency for getting NoteService instance."""
    repository = AttachmentRepository(session)
    return AttachmentService(repository)


@router.post(
    "",
    response_model=AttachmentResponse,  # 返回新创建的附件信息
    status_code=status.HTTP_201_CREATED,
    summary="[Attachments] Upload an attachment for a specific note",  # 添加 OpenAPI 描述
)
async def upload_note_attachment(
    file: Annotated[
        UploadFile, File(..., title="Attachment of Note", description="Upload a file")
    ],  # 使用 FastAPI 的 UploadFile 来接收文件
    note_id: int,
    attachment_service: AttachmentService = Depends(get_attachment_service),
    note_service: NoteService = Depends(get_note_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        # 1. 验证 Note 是否存在且属于当前用户
        note = await note_service.get_note(note_id=note_id, current_user=current_user)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or insufficient permissions",
            )

        # 2. 上传附件
        created_attachment = await attachment_service.add_attachment_to_note(
            file=file, note_id=note_id, current_user=current_user
        )
        logger.info(f"Uploaded attachment {created_attachment.id} for note {note_id}")
        return created_attachment  # 返回创建的附件信息

    except HTTPException as http_exc:
        raise http_exc  # 重新抛出已知的 HTTP 异常
    except Exception as e:
        logger.error(f"Failed to upload attachment for note {note_id}: {str(e)}")
        # 在生产环境中，避免暴露详细错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload attachment",
        )
