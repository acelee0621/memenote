from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.utils.migrations import run_migrations
from app.routes import user_routes



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


app.include_router(user_routes.router)  # Users Router



@app.get("/health")
async def health_check(response: Response):
    response.status_code = 200
    return {"status": "ok 👍 "}
