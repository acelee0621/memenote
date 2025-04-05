from sqlalchemy import select, desc, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.models import Attachment
from app.schemas.schemas import AttachmentCreate


class AttachmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, data: AttachmentCreate, note_id: int, current_user
    ) -> Attachment:
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

    async def get_by_id(
        self, attachment_id: int, note_id: int, current_user
    ) -> Attachment:
        query = select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.note_id == note_id,
            Attachment.user_id == current_user.id,
        )
        result = await self.session.scalars(query)
        attachment = result.one_or_none()
        if not attachment:
            raise NotFoundException(f"Attachment with id {attachment_id} not found")
        return attachment

    async def get_all(
        self,
        note_id: int,
        limit: int,
        offset: int,
        order_by: str | None,
        current_user,
    ) -> list[Attachment]:
        query = select(Attachment).where(
            Attachment.note_id == note_id, Attachment.user_id == current_user.id
        )
        
        if order_by:
            if order_by == "created_at desc":
                query = query.order_by(desc(Attachment.created_at))
            elif order_by == "created_at asc":
                query = query.order_by(asc(Attachment.created_at))

        # 分页功能
        query = query.limit(limit).offset(offset)

        result = await self.session.scalars(query)
        return list(result.all())

    async def delete(self, attachment_id: int, current_user) -> None:
        
        attachment = await self.session.get(Attachment, attachment_id)

        if not attachment or attachment.user_id != current_user.id:
            raise NotFoundException(f"Attachment with id {attachment_id} not found")

        await self.session.delete(attachment)
        await self.session.commit()
