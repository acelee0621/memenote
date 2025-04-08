from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.core.database import get_db
from app.core.security import get_current_user
from app.repository.tag_repo import TagRepository
from app.service.tag_service import TagService
from app.schemas.schemas import (
    TagCreate,
    TagUpdate,
    TagResponse,
    UserResponse,
)
from app.schemas.param_schemas import TagQueryParams



# Set up logger for this module
logger = get_logger(__name__)


router = APIRouter(
    prefix="/tags", tags=["Tags"], dependencies=[Depends(get_current_user)]
)



def get_tag_service(session: AsyncSession = Depends(get_db)) -> TagService:
    """Dependency for getting TagService instance."""
    repository = TagRepository(session)
    return TagService(repository)


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    service: TagService = Depends(get_tag_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TagResponse:
    """Create new tag."""
    try:
        created_tag = await service.create_tag(data=data, current_user=current_user)
        logger.info(f"Created tag {created_tag.id}")
        return created_tag
    except Exception as e:
        logger.error(f"Failed to create tag: {str(e)}")
        raise


@router.get("", response_model=list[TagResponse])
async def get_all_tags(
    params: Annotated[TagQueryParams, Query()],
    service: TagService = Depends(get_tag_service),
    current_user: UserResponse = Depends(get_current_user),
) -> list[TagResponse]:
    """Get all tags."""
    try:
        all_tags = await service.get_tags(
            search=params.search,
            order_by=params.order_by,
            limit=params.limit,
            offset=params.offset,
            current_user=current_user,
        )
        logger.info(f"Retrieved {len(all_tags)} tags")
        return all_tags
    except Exception as e:
        logger.error(f"Failed to fetch all tags: {str(e)}")
        raise


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    service: TagService = Depends(get_tag_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TagResponse:
    """Get tag by id."""
    try:
        tag = await service.get_tag(tag_id=tag_id, current_user=current_user)
        logger.info(f"Retrieved tag {tag_id}")
        return tag
    except Exception as e:
        logger.error(f"Failed to get tag {tag_id}: {str(e)}")
        raise


@router.patch("/{tag_id}", response_model=TagResponse, status_code=status.HTTP_200_OK)
async def update_tag(
    data: TagUpdate,
    tag_id: int,
    service: TagService = Depends(get_tag_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TagResponse:
    """Update tag."""
    try:
        updated_tag = await service.update_tag(
            data=data, tag_id=tag_id, current_user=current_user
        )
        logger.info(f"Updated tag {tag_id}")
        return updated_tag
    except Exception as e:
        logger.error(f"Failed to update tag {tag_id}: {str(e)}")
        raise


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    service: TagService = Depends(get_tag_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete tag."""
    try:
        await service.delete_tag(tag_id=tag_id, current_user=current_user)
        logger.info(f"Deleted tag {tag_id}")
    except Exception as e:
        logger.error(f"Failed to delete tag {tag_id}: {str(e)}")
        raise
