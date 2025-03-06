from app.repository.note_repo import NoteRepository
from app.schemas.schemas import NoteCreate, NoteUpdate, NoteResponse


class NoteService:
    def __init__(self, repository: NoteRepository):
        """Service layer for note operations."""

        self.repository = repository

    async def create_note(self, data: NoteCreate, current_user) -> NoteResponse:
        """
        Asynchronously creates a new note for the current user.
        Args:
            data (NoteCreate): The data required to create a new note.
            current_user: The user who is creating the note.
        Returns:
            NoteResponse: The response model containing the created note's details.
        """
        new_note = await self.repository.create(data, current_user)
        return NoteResponse.model_validate(new_note)

    async def get_note(self, note_id: int, current_user) -> NoteResponse:
        """
        Retrieve a note by its ID for the current user.
        Args:
            note_id (int): The ID of the note to retrieve.
            current_user: The user requesting the note.
        Returns:
            NoteResponse: The response model containing the note details.
        """
        note = await self.repository.get_by_id(note_id, current_user)
        return NoteResponse.model_validate(note)

    async def get_notes(
        self,
        search: str | None,
        order_by: str | None,
        limit: int,
        offset: int,
        current_user,
    ) -> list[NoteResponse]:
        """
        Asynchronously retrieves a list of notes for the current user.
        Args:
            current_user: The user for whom to retrieve the notes.
        Returns:
            list[NoteResponse]: A list of NoteResponse objects representing the user's notes.
        """
        notes = await self.repository.get_all(
            search=search,
            order_by=order_by,
            limit=limit,
            offset=offset,
            current_user=current_user,
        )
        return [NoteResponse.model_validate(note) for note in notes]

    async def update_note(
        self, data: NoteUpdate, note_id: int, current_user
    ) -> NoteResponse:
        """
        Asynchronously updates a note for the current user.
        Args:
            data (NoteUpdate): The data to update the note with.
            note_id (int): The ID of the note to update.
            current_user: The user who is updating the note.
        Returns:
            NoteResponse: The response model containing the updated note's details.
        """
        note = await self.repository.update(data, note_id, current_user)
        return NoteResponse.model_validate(note)

    async def delete_note(self, note_id: int, current_user) -> None:
        """
        Asynchronously deletes a note with the given note_id for the current user.
        Args:
            note_id (int): The ID of the note to be deleted.
            current_user: The user who is requesting the deletion.
        Returns:
            None
        """
        await self.repository.delete(note_id, current_user)
