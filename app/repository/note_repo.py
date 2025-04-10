from datetime import datetime, timedelta, timezone

from sqlalchemy import select, desc, asc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.models import Note, Tag, NoteTag
from app.schemas.schemas import NoteCreate, NoteUpdate


class NoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: NoteCreate, current_user) -> Note:
        """
        Create a new note in the database.
        Args:
            data (NoteCreate): The note data containing title and content.
            current_user: The current authenticated user.
        Returns:
            Note: The newly created note object.
        Raises:
            AlreadyExistsException: If a note with the same title already exists.
        """
        new_note = Note(title=data.title, content=data.content, user_id=current_user.id)
        self.session.add(new_note)
        try:
            await self.session.commit()
            await self.session.refresh(new_note)
            return new_note
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(
                f"Note with content {data.content} already exists"
            )

    async def get_by_id(self, note_id: int, current_user) -> Note:
        """
        Retrieves a note by its ID for the current user.
        Args:
            note_id (int): The ID of the note to retrieve
            current_user: The current authenticated user
        Returns:
            Note: The note object if found
        Raises:
            NotFoundException: If note with given ID doesn't exist for current user
        """
        query = (
            select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
            # .options(selectinload(Note.todos),selectinload(Note.reminders))  #  models里定义了lazy属性就无需这条
        )
        result = await self.session.scalars(query)
        note = result.one_or_none()
        if not note:
            raise NotFoundException(f"Note with id {note_id} not found")
        return note

    async def get_all(
        self,
        search: str | None,
        order_by: str | None,
        tag_id: int | None,
        limit: int,
        offset: int,
        current_user,
    ) -> list[Note]:
        query = select(Note).where(Note.user_id == current_user.id)

        if tag_id is not None:
            tag_query = select(Tag).where(
                Tag.id == tag_id, Tag.user_id == current_user.id
            )
            tag_result = await self.session.scalars(tag_query)
            tag = tag_result.one_or_none()
            if not tag:
                raise NotFoundException(f"Tag with id {tag_id} not found")
            query = query.join(NoteTag).join(Tag).where(Tag.id == tag_id)

        if search:
            query = query.where(
                or_(Note.content.ilike(f"%{search}%"), Note.title.ilike(f"%{search}%"))
            )

        if order_by:
            if order_by == "created_at desc":
                query = query.order_by(desc(Note.created_at))
            elif order_by == "created_at asc":
                query = query.order_by(asc(Note.created_at))

        # 分页功能
        query = query.limit(limit).offset(offset)

        result = await self.session.scalars(query)
        return list(result.all())

    async def update(self, data: NoteUpdate, note_id: int, current_user) -> Note:
        """
        Update a note with the given data for the current user.
        Args:
            data (NoteUpdate): The data to update the note with.
            note_id (int): The ID of the note to update.
            current_user: The current user performing the update.
        Returns:
            Note: The updated note.
        Raises:
            NotFoundException: If the note with the given ID is not found or does not belong to the current user.
            ValueError: If there are no fields to update.
        """
        query = select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
        result = await self.session.scalars(query)
        note = result.one_or_none()
        if not note:
            raise NotFoundException(
                f"Note with id {note_id} not found or does not belong to the current user"
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        # 确保不修改 id 和 user_id
        update_data.pop("id", None)
        update_data.pop("user_id", None)
        if not update_data:
            raise ValueError("No fields to update")
        for key, value in update_data.items():
            setattr(note, key, value)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def delete(self, note_id: int, current_user) -> None:
        """
        Deletes a note from the repository.
        Args:
            note_id (int): The ID of the note to be deleted.
            current_user: The user who is attempting to delete the note.
        Raises:
            NotFoundException: If the note does not exist or the note does not belong to the current user.
        Returns:
            None
        """
        note = await self.session.get(Note, note_id)

        if not note or note.user_id != current_user.id:
            raise NotFoundException(f"Note with id {note_id} not found")

        await self.session.delete(note)
        await self.session.commit()

    async def add_tag_to_note(self, note_id: int, tag_id: int, current_user) -> Note:
        """
        Add a tag to a specific note for the current user.
        Args:
            note_id (int): The ID of the note.
            tag_id (int): The ID of the tag to add.
            current_user: The current authenticated user.
        Returns:
            Note: The updated note object.
        Raises:
            NotFoundException: If note or tag not found.
            AlreadyExistsException: If tag is already associated with the note.
        """

        note = await self.get_by_id(note_id, current_user)

        query = select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
        result = await self.session.scalars(query)
        tag = result.one_or_none()
        if not tag:
            raise NotFoundException(f"Tag with id {tag_id} not found")

        if tag in note.tags:
            raise AlreadyExistsException(
                f"Tag with id {tag_id} already associated with note {note_id}"
            )

        note.tags.append(tag)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def remove_tag_from_note(
        self, note_id: int, tag_id: int, current_user
    ) -> Note:
        """
        Remove a tag from a specific note for the current user.
        Args:
            note_id (int): The ID of the note.
            tag_id (int): The ID of the tag to remove.
            current_user: The current authenticated user.
        Returns:
            Note: The updated note object.
        Raises:
            NotFoundException: If note or tag not found, or tag not associated.
        """

        note = await self.get_by_id(note_id, current_user)

        query = select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
        result = await self.session.scalars(query)
        tag = result.one_or_none()
        if not tag:
            raise NotFoundException(f"Tag with id {tag_id} not found")

        if tag not in note.tags:
            raise NotFoundException(
                f"Tag with id {tag_id} not associated with note {note_id}"
            )

        note.tags.remove(tag)
        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def enable_share(self, note_id: int, expires_in: int, current_user) -> Note:
        note = await self.get_by_id(note_id, current_user)
        # 生成 share_code 和过期时间
        note.generate_share_code()
        note.share_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in
        )

        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def disable_share(self, note_id: int, current_user) -> Note:
        note = await self.get_by_id(note_id, current_user)
        # 清除分享信息
        note.share_code = None # type: ignore
        note.share_expires_at = None # type: ignore

        await self.session.commit()
        await self.session.refresh(note)
        return note

    async def get_by_share_code(self, share_code: str) -> Note:
        query = select(Note).where(Note.share_code == share_code)
        result = await self.session.scalars(query)
        note = result.one_or_none()

        if not note:
            raise NotFoundException("Note not found or sharing not enabled")

        # 检查是否过期
        if note.share_expires_at and note.share_expires_at < datetime.now(timezone.utc):
            raise NotFoundException("Share link has expired")

        return note
