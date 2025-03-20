from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware


from app.core.config import settings
from app.core.logging import setup_logging
from app.utils.migrations import run_migrations
from app.routes import (
    user_routes,
    note_routes,
    todo_routes,
    reminder_routes,
    auth_routes,
    ws,
    sse,
)


# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
run_migrations()


app = FastAPI(title=settings.app_name, version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)  # Auth Router
app.include_router(user_routes.router)  # Users Router
app.include_router(note_routes.router)  # Notes Router
app.include_router(todo_routes.router)  # Todos Router
app.include_router(reminder_routes.router)  # Reminders Router
app.include_router(ws.router)  # WebSocket Router
app.include_router(sse.router)  # SSE Router


@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}
