from sqlalchemy import select, desc, asc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.models import Attachment
from app.schemas.schemas import AttachmentCreate, AttachmentUpdate


class AttachmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: AttachmentCreate, note_id: int, current_user) -> Attachment:
        new_attachment = Attachment(
            object_name=data.object_name,
            bucket_name=data.bucket_name,
            original_filename=data.original_filename,
            content_type=data.content_type,
            size=data.size,
            note_id=note_id,
            user_id=current_user.id,
        )
        self.session.add(new_attachment)
        try:
            await self.session.commit()
            await self.session.refresh(new_attachment)
            return new_attachment
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(
                f"Attachment with content {data.original_filename} already exists"
            )

    
