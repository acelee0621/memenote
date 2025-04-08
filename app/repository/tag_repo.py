from sqlalchemy import select, desc, asc, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.models import Tag
from app.schemas.schemas import TagCreate, TagUpdate


class TagRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: TagCreate, current_user) -> Tag:
        new_tag = Tag(name=data.name, user_id=current_user.id)
        self.session.add(new_tag)
        try:
            await self.session.commit()
            await self.session.refresh(new_tag)
            return new_tag
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(f"Tag with name {data.name} already exists")

    async def get_by_id(self, tag_id: int, current_user) -> Tag:
        query = select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
        result = await self.session.scalars(query)
        tag = result.one_or_none()
        if not tag:
            raise NotFoundException(f"Tag with id {tag_id} not found")
        return tag
    
    async def get_by_name(self, name: str, current_user) -> Tag:
        query = select(Tag).where(Tag.name == name, Tag.user_id == current_user.id)
        result = await self.session.scalars(query)
        tag = result.one_or_none()
        if not tag:
            raise NotFoundException(f"Tag with name {name} not found")
        return tag

    async def get_all(
        self,
        search: str | None,
        order_by: str | None,
        limit: int,
        offset: int,
        current_user,
    ) -> list[Tag]:
        query = select(Tag).where(Tag.user_id == current_user.id)

        if search:
            query = query.where(Tag.name.ilike(f"%{search}%"))

        if order_by:
            if order_by == "created_at desc":
                query = query.order_by(desc(Tag.created_at))
            elif order_by == "created_at asc":
                query = query.order_by(asc(Tag.created_at))

        # 分页功能
        query = query.limit(limit).offset(offset)

        result = await self.session.scalars(query)
        return list(result.all())

    async def update(self, data: TagUpdate, tag_id: int, current_user) -> Tag:
        query = select(Tag).where(Tag.id == tag_id, Tag.user_id == current_user.id)
        result = await self.session.scalars(query)
        tag = result.one_or_none()
        if not tag:
            raise NotFoundException(
                f"Tag with id {tag_id} not found or does not belong to the current user"
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        # 确保不修改 id 和 user_id
        update_data.pop("id", None)
        update_data.pop("user_id", None)
        if not update_data:
            raise ValueError("No fields to update")
        for key, value in update_data.items():
            setattr(tag, key, value)
        await self.session.commit()
        await self.session.refresh(tag)
        return tag

    async def delete(self, tag_id: int, current_user) -> None:
        tag = await self.session.get(Tag, tag_id)

        if not tag or tag.user_id != current_user.id:
            raise NotFoundException(f"Tag with id {tag_id} not found")

        await self.session.delete(tag)
        await self.session.commit()
