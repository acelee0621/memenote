from sqlalchemy import select, desc, asc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.models import Attachment, Note
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

    async def get_by_id(self, attachment_id: int, current_user) -> Note:
        query = (
            select(Attachment).where(Attachment.id == attachment_id, Attachment.user_id == current_user.id)           
        )
        result = await self.session.scalars(query)
        note = result.one_or_none()
        if not note:
            raise NotFoundException(f"Attachment with id {attachment_id} not found")
        return note

    # async def get_all(
    #     self,
    #     search: str | None,
    #     order_by: str | None,
    #     limit: int,
    #     offset: int,
    #     current_user,
    # ) -> list[Note]:
    #     query = select(Note).where(Note.user_id == current_user.id)

    #     if search:
    #         query = query.where(
    #             or_(Note.content.ilike(f"%{search}%"), Note.title.ilike(f"%{search}%"))
    #         )

    #     if order_by:
    #         if order_by == "created_at desc":
    #             query = query.order_by(desc(Note.created_at))
    #         elif order_by == "created_at asc":
    #             query = query.order_by(asc(Note.created_at))

    #     # 分页功能
    #     query = query.limit(limit).offset(offset)

    #     result = await self.session.scalars(query)
    #     return list(result.all())

    # async def update(self, data: NoteUpdate, note_id: int, current_user) -> Note:
    #     query = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    #     result = await self.session.scalars(query)
    #     note = result.one_or_none()
    #     if not note:
    #         raise NotFoundException(
    #             f"Note with id {note_id} not found or does not belong to the current user"
    #         )
    #     update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    #     # 确保不修改 id 和 user_id
    #     update_data.pop("id", None)
    #     update_data.pop("user_id", None)
    #     if not update_data:
    #         raise ValueError("No fields to update")
    #     for key, value in update_data.items():
    #         setattr(note, key, value)
    #     await self.session.commit()
    #     await self.session.refresh(note)
    #     return note

    # async def delete(self, note_id: int, current_user) -> None:
    #     note = await self.session.get(Note, note_id)

    #     if not note or note.user_id != current_user.id:
    #         raise NotFoundException(f"Note with id {note_id} not found")

    #     await self.session.delete(note)  # 触发 ORM 级联删除
    #     await self.session.commit()
