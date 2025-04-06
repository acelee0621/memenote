import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError

from app.core.logging import get_logger
from app.core.config import settings
from app.core.s3_client import s3_client
from app.core.exceptions import NotFoundException, ForbiddenException
from app.repository.attachment_repo import AttachmentRepository
from app.schemas.schemas import (
    AttachmentCreate,
    AttachmentResponse,
    PresignedUrlResponse,
)

logger = get_logger(__name__)


class AttachmentService:
    def __init__(self, repository: AttachmentRepository):
        """Service layer for attachment operations."""

        self.repository = repository

    async def add_attachment_to_note(
        self, file: UploadFile, note_id: int, current_user
    ) -> AttachmentResponse:
        # ===== 1. 文件元数据处理,从 UploadFile 获取文件元数据 =====
        original_filename = file.filename or f"unnamed_{uuid.uuid4()}"
        content_type = file.content_type or "application/octet-stream"

        try:
            file.file.seek(0, 2)  # 移动到文件末尾以获取大小
            size = file.file.tell()  # 获取文件大小
            file.file.seek(0)  # 重置文件指针到开头以供上传
        except (AttributeError, OSError) as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid file stream: {str(e)}"
            )

        # ===== 2. 生成唯一的 object_name 对象名称（使用 UUID + 文件扩展名） =====
        file_extension = (
            original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
        )
        object_name = f"attachments/{uuid.uuid4()}.{file_extension}"

        # ===== 3. 使用 boto3 上传文件到 MinIO =====
        try:
            s3_client.upload_fileobj(
                Fileobj=file.file,
                Bucket=settings.MINIO_BUCKET,
                Key=object_name,
                ExtraArgs={"ContentType": content_type},
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "UnknownError")
            logger.error(
                f"Failed to upload file {original_filename}: {error_code} - {str(e)}"
            )
            match error_code:
                case "NoSuchBucket":
                    raise NotFoundException("Storage bucket does not exist")
                case "AccessDenied":
                    raise ForbiddenException("Permission denied to upload file")
                case _:
                    raise HTTPException(
                        status_code=500, detail=f"S3 upload failed: {str(e)}"
                    )
        except Exception as e:
            logger.error(
                f"Unexpected error uploading file {original_filename}: {str(e)}"
            )
            raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

        # ===== 4. 构造 AttachmentCreate 数据,并在数据库中创建记录 =====

        attachment_data = AttachmentCreate(
            note_id=note_id,
            object_name=object_name,
            bucket_name=settings.MINIO_BUCKET,
            original_filename=original_filename,
            content_type=content_type,
            size=size,
        )
        try:
            new_attachment = await self.repository.create(
                attachment_data, note_id, current_user
            )
            return AttachmentResponse.model_validate(new_attachment)
        except Exception as e:
            # 数据库失败后尝试清理已上传的文件
            try:
                s3_client.delete_object(Bucket=settings.MINIO_BUCKET, Key=object_name)
                logger.info(
                    f"Cleaned up orphaned file {object_name} after database failure"
                )
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up {object_name}: {str(cleanup_error)}")
            raise HTTPException(
                status_code=500, detail=f"Failed to save attachment: {str(e)}"
            )

    async def get_attachment(
        self, attachment_id: int, note_id: int, current_user
    ) -> AttachmentResponse:
        attachment = await self.repository.get_by_id(
            attachment_id, note_id, current_user
        )
        return AttachmentResponse.model_validate(attachment)

    async def get_attachments(
        self,
        note_id: int,
        order_by: str | None,
        limit: int,
        offset: int,
        current_user,
    ) -> list[AttachmentResponse]:
        attachments = await self.repository.get_all(
            note_id=note_id,
            order_by=order_by,
            limit=limit,
            offset=offset,
            current_user=current_user,
        )
        return [
            AttachmentResponse.model_validate(attachment) for attachment in attachments
        ]

    async def delete_attachment(
        self, attachment_id: int, note_id: int, current_user
    ) -> None:
        # 先删除数据库记录
        attachment = await self.get_attachment(
            attachment_id=attachment_id, note_id=note_id, current_user=current_user
        )
        await self.repository.delete(attachment.id, current_user)
        logger.info(f"Deleted attachment record {attachment_id} from database")

        # 再删除文件
        try:
            s3_client.delete_object(
                Bucket=attachment.bucket_name, Key=attachment.object_name
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"Failed to delete attachment {attachment_id}: {error_code} - {str(e)}"
            )
            # TODO: 可选择记录到日志或队列，异步清理，优化一致性
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error deleting attachment {attachment_id}: {str(e)}",
            )

    async def download_attachment(self, attachment_id: int, note_id: int, current_user):
        attachment = await self.get_attachment(
            attachment_id=attachment_id, note_id=note_id, current_user=current_user
        )

        try:
            s3_response = s3_client.get_object(
                Bucket=attachment.bucket_name, Key=attachment.object_name
            )
            file_stream = s3_response["Body"]
            safe_filename = quote(attachment.original_filename)
            return StreamingResponse(
                content=file_stream,
                media_type=attachment.content_type,
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}"
                },
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"Failed to download attachment {attachment_id}: {error_code} - {str(e)}"
            )
            match error_code:
                case "NoSuchKey":
                    raise NotFoundException("File not found in storage")
                case "AccessDenied":
                    raise ForbiddenException("Permission denied to access file")
                case _:
                    raise HTTPException(
                        status_code=500, detail="Failed to download file"
                    )
        except Exception as e:
            logger.error(
                f"Unexpected error downloading attachment {attachment_id}: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

    async def get_presigned_url(
        self, attachment_id: int, note_id: int, current_user
    ) -> PresignedUrlResponse:
        attachment = await self.get_attachment(
            attachment_id=attachment_id, note_id=note_id, current_user=current_user
        )
        expires_in = 60 * 60 * 24  # 24小时
        try:
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": attachment.bucket_name,
                    "Key": attachment.object_name,
                },
                ExpiresIn=expires_in,
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                f"Failed to generate presigned URL for attachment {attachment_id}: {error_code}"
            )
            match error_code:
                case "NoSuchKey":
                    raise NotFoundException("File not found in storage")
                case "AccessDenied":
                    raise ForbiddenException("Permission denied to access file")
                case _:
                    raise HTTPException(
                        status_code=500, detail="Failed to generate presigned URL"
                    )

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return PresignedUrlResponse(
            url=presigned_url,
            expires_at=expires_at,
            filename=attachment.original_filename,
            content_type=attachment.content_type,
            size=attachment.size,
            attachment_id=attachment_id,
        )
