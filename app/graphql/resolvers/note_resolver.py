from app.service.note_service import NoteService
from app.repository.note_repo import NoteRepository
from app.graphql.types.type import Note


def get_note_service(session) -> NoteService:
    """Dependency for getting NoteService instance."""
    repository = NoteRepository(session)
    return NoteService(repository)


async def resolve_notes(db, current_user) -> list[Note]:
    service = get_note_service(session=db)
    return await service.get_notes(search=None,order_by=None,limit=20,offset=0,current_user=current_user)