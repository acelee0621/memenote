from typing import Annotated, Union

from fastapi import APIRouter, Depends, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.core.dependencies import get_attachment_note_id
from app.service.attachment_service import AttachmentService
from app.repository.attachment_repo import AttachmentRepository
from app.schemas.schemas import UserResponse, AttachmentResponse, PresignedUrlResponse
from app.schemas.param_schemas import AttachmentQueryParams


logger = get_logger(__name__)


router = APIRouter(prefix="/{note_id}/attachments")


def get_attachment_service(
    session: AsyncSession = Depends(get_db),
) -> AttachmentService:
    """Dependency for getting NoteService instance."""
    repository = AttachmentRepository(session)
    return AttachmentService(repository)


@router.post(
    "",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="[Attachments] Upload an attachment for a specific note",
)
async def upload_note_attachment(
    file: Annotated[
        UploadFile, File(..., title="Attachment of Note", description="Upload a file")
    ],
    note_id: Annotated[int, Depends(get_attachment_note_id)],
    service: AttachmentService = Depends(get_attachment_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        # 1. 验证 Note 是否存在且属于当前用户,note_id已由依赖项get_note_id验证并提供
        # 2. 上传附件
        created_attachment = await service.add_attachment_to_note(
            file=file, note_id=note_id, current_user=current_user
        )
        logger.info(f"Uploaded attachment {created_attachment.id} for note {note_id}")
        return created_attachment  # 返回创建的附件信息
    except Exception as e:
        logger.error(f"Failed to upload attachment for note {note_id}: {str(e)}")
        raise


@router.get(
    "/{attachment_id}/download",
    response_class=StreamingResponse,
    summary="[Attachments] Download an attachment directly",
)
async def download_attachment(
    note_id: Annotated[int, Depends(get_attachment_note_id)],
    attachment_id: int,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        response = await service.download_attachment(
            attachment_id=attachment_id, note_id=note_id, current_user=current_user
        )
        return response
    except Exception as e:
        logger.error(f"Failed to download attachment {attachment_id}: {str(e)}")
        raise


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[Attachments] Delete an attachment",
)
async def delete_attachment(
    note_id: Annotated[int, Depends(get_attachment_note_id)],
    attachment_id: int,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        await service.delete_attachment(
            attachment_id=attachment_id, note_id=note_id, current_user=current_user
        )
        logger.info(f"Deleted attachment {attachment_id}")
    except Exception as e:
        logger.error(f"Failed to delete attachment {attachment_id}: {str(e)}")
        raise


@router.get(
    "",
    response_model=list[AttachmentResponse],
    summary="[Attachments] Get all attachments",
)
async def get_all_attachments(
    params: Annotated[AttachmentQueryParams, Query()],
    note_id: Annotated[int, Depends(get_attachment_note_id)],
    service: AttachmentService = Depends(get_attachment_service),
    current_user: UserResponse = Depends(get_current_user),
) -> list[AttachmentResponse]:
    try:
        all_attachments = await service.get_attachments(
            note_id=note_id,
            order_by=params.order_by,
            limit=params.limit,
            offset=params.offset,
            current_user=current_user,
        )
        logger.info(f"Retrieved {len(all_attachments)} attachments")
        return all_attachments
    except Exception as e:
        logger.error(f"Failed to fetch all attachments: {str(e)}")
        raise


@router.get(
    "/{attachment_id}",
    response_model=Union[AttachmentResponse, PresignedUrlResponse],
    summary="[Attachments] Get attachment by id or pre-signed URL",
)
async def get_attachment(
    attachment_id: int,
    note_id: Annotated[int, Depends(get_attachment_note_id)],
    presigned: Annotated[
        bool, Query(description="If true, return pre-signed URL")
    ] = False,
    service: AttachmentService = Depends(get_attachment_service),
    current_user: UserResponse = Depends(get_current_user),
) -> Union[AttachmentResponse, PresignedUrlResponse]:
    if presigned:
        try:
            response = await service.get_presigned_url(
                attachment_id, note_id, current_user
            )
            logger.info(f"Generated pre-signed URL for attachment {attachment_id}")
            return response
        except Exception as e:
            logger.error(
                f"Failed to get pre-signed URL for attachment {attachment_id}: {str(e)}"
            )
            raise
    else:
        try:
            attachment = await service.get_attachment(
                attachment_id=attachment_id,
                note_id=note_id,
                current_user=current_user,
            )
            logger.info(f"Retrieved attachment {attachment_id}")
            return attachment
        except Exception as e:
            logger.error(f"Failed to get attachment {attachment_id}: {str(e)}")
            raise
