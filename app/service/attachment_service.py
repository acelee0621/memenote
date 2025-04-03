import uuid

from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError

from app.repository.attachment_repo import AttachmentRepository
from app.schemas.schemas import AttachmentCreate, AttachmentResponse
from app.core.s3_client import s3_client
from app.core.config import settings


class AttachmentService:
    def __init__(self, repository: AttachmentRepository):
        """Service layer for attachment operations."""

        self.repository = repository

    async def add_attachment_to_note(self, file: UploadFile, note_id: int, current_user) -> AttachmentResponse:
        try:
            # ===== 1. 文件元数据处理,从 UploadFile 获取文件元数据 =====
            original_filename = file.filename or f"unnamed_{uuid.uuid4()}"
            content_type = file.content_type or "application/octet-stream"

            try:
                file.file.seek(0, 2)  # 移动到文件末尾以获取大小
                size = file.file.tell()  # 获取文件大小
                file.file.seek(0)  # 重置文件指针到开头以供上传
            except (AttributeError, OSError) as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file stream: {str(e)}"
                )

            # ===== 2. 生成唯一的 object_name 对象名称（使用 UUID + 文件扩展名） =====
            try:
                file_extension = original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
                object_name = f"attachments/{uuid.uuid4()}.{file_extension}"
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate object name: {str(e)}"
                )

            # ===== 3. 使用 boto3 上传文件到 MinIO =====
            try:
                s3_client.upload_fileobj(
                    Fileobj=file.file,
                    Bucket=settings.MINIO_BUCKET,
                    Key=object_name,
                    ExtraArgs={"ContentType": content_type}
                )
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "UnknownError")
                match error_code:
                    case "NoSuchBucket":
                        raise HTTPException(
                            status_code=404,
                            detail=f"Bucket '{settings.MINIO_BUCKET}' does not exist"
                        )
                    case "AccessDenied":
                        raise HTTPException(
                            status_code=403,
                            detail="Permission denied to upload file"
                        )
                    case _: 
                        raise HTTPException(
                            status_code=500,
                            detail=f"S3 upload failed: {str(e)}"
                        )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"File upload error: {str(e)}"
                )

            # ===== 4. 构造 AttachmentCreate 数据,并在数据库中创建记录 =====
            try:
                attachment_data = AttachmentCreate(
                    note_id=note_id,
                    object_name=object_name,
                    bucket_name=settings.MINIO_BUCKET,
                    original_filename=original_filename,
                    content_type=content_type,
                    size=size
                )
                new_attachment = await self.repository.create(attachment_data, note_id, current_user)
                return AttachmentResponse.model_validate(new_attachment)
            except Exception as e:
                # 数据库失败后尝试清理已上传的文件
                try:
                    s3_client.delete_object(
                        Bucket=settings.MINIO_BUCKET,
                        Key=object_name
                    )
                except Exception:
                    pass  # 清理失败不影响主错误

                raise HTTPException(
                    status_code=500,
                    detail=f"Database operation failed: {str(e)}"
                )

        except HTTPException:
            raise  # 直接传递已处理的HTTP异常
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error: {str(e)}"
            )
    