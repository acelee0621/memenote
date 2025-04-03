import uuid
from fastapi import UploadFile
from app.repository.attachment_repo import AttachmentRepository
from app.schemas.schemas import AttachmentCreate, AttachmentResponse
from app.core.s3_client import s3_client
from app.core.config import settings


class AttachmentService:
    def __init__(self, repository: AttachmentRepository):
        """Service layer for attachment operations."""

        self.repository = repository

    async def add_attachment_to_note(self, file: UploadFile, note_id: int, current_user) -> AttachmentResponse:
        # 1. 从 UploadFile 获取文件元数据
        original_filename = file.filename or f"unnamed_{uuid.uuid4()}"
        content_type = file.content_type or "application/octet-stream"
        file.file.seek(0, 2)  # 移动到文件末尾以获取大小
        size = file.file.tell()  # 获取文件大小
        file.file.seek(0)  # 重置文件指针到开头以供上传

        # 2. 生成唯一的 object_name（例如使用 UUID + 文件扩展名）
        file_extension = original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
        object_name = f"attachments/{uuid.uuid4()}.{file_extension}"

        # 3. 使用 boto3 上传文件到 MinIO
        s3_client.upload_fileobj(
            Fileobj=file.file,  # 文件流
            Bucket=settings.MINIO_BUCKET,  # 存储桶名称
            Key=object_name,  # 对象名称
            ExtraArgs={"ContentType": content_type}  # 设置 MIME 类型
        )

        # 4. 构造 AttachmentCreate 数据
        attachment_data = AttachmentCreate(
            note_id=note_id,
            object_name=object_name,
            bucket_name=settings.MINIO_BUCKET,
            original_filename=original_filename,
            content_type=content_type,
            size=size
        )

        # 5. 在数据库中创建记录
        new_attachment = await self.repository.create(attachment_data, note_id, current_user)
        return AttachmentResponse.model_validate(new_attachment)

    