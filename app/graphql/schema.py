import strawberry
from app.graphql.queries import Query


schema = strawberry.Schema(query=Query)