from app.repository.tag_repo import TagRepository
from app.schemas.schemas import TagCreate, TagUpdate, TagResponse


class TagService:
    def __init__(self, repository: TagRepository):
        """Service layer for tag operations."""

        self.repository = repository

    async def create_tag(self, data: TagCreate, current_user) -> TagResponse:
        
        new_tag = await self.repository.create(data, current_user)
        return TagResponse.model_validate(new_tag)

    async def get_tag(self, tag_id: int, current_user) -> TagResponse:
        
        tag = await self.repository.get_by_id(tag_id, current_user)        
        return TagResponse.model_validate(tag)

    async def get_tags(
        self,
        search: str | None,
        order_by: str | None,
        limit: int,
        offset: int,
        current_user,
    ) -> list[TagResponse]:
        
        tags = await self.repository.get_all(
            search=search,
            order_by=order_by,
            limit=limit,
            offset=offset,
            current_user=current_user,
        )
        
        return [TagResponse.model_validate(tag) for tag in tags]

    async def update_tag(
        self, data: TagUpdate, tag_id: int, current_user
    ) -> TagResponse:
        
        tag = await self.repository.update(data, tag_id, current_user)
        return TagResponse.model_validate(tag)

    async def delete_tag(self, tag_id: int, current_user) -> None:
        
        await self.repository.delete(tag_id, current_user)
