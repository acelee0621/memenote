import strawberry

from app.graphql.types.type import User, Note, Todo, Reminder
from app.graphql.resolvers.note_resolver import resolve_notes


@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: int) -> User | None:        
        pass
    
    # @strawberry.field
    # async def users(self) -> list[User]:
    #     # 例如: return await db.execute(select(User)).all()
    #     pass
    
    # @strawberry.field
    # async def note(self, id: int) -> Note | None:
    #     # 例如: return await db.get(Note, id)
    #     pass
    
    @strawberry.field
    async def notes(self, info:strawberry.Info) -> list[Note]:
        db = info.context["db"]
        current_user = info.context["current_user"]
        return await resolve_notes(db, current_user)
    
    # @strawberry.field
    # async def todo(self, id: int) -> Todo | None:    
    #     pass
    
    # @strawberry.field
    # async def todos(self, 
    #                user_id: int | None = None, 
    #                note_id: int | None = None) -> list[Todo]:    
    #     pass
    
    # @strawberry.field
    # async def reminder(self, id: int) -> Reminder | None:    
    #     pass
    
    # @strawberry.field
    # async def reminders(self, 
    #                    user_id: int | None = None, 
    #                    note_id: int | None = None) -> list[Reminder]:    
    #     pass