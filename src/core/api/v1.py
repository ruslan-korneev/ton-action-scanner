from fastapi import FastAPI
from sqlalchemy import text

from src.core.config import settings
from src.core.dependencies.db import AsyncSessionDep

__all__ = ("app",)

app = FastAPI(
    debug=settings.logging_level == "DEBUG",
    title=settings.project_title,
    description=settings.project_description,
    version="1.0.0",
)


@app.get("/health")
async def health_route(session: AsyncSessionDep) -> None:
    await session.execute(text("SELECT 1"))
