import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from src.settings import settings

logger = logging.getLogger(__name__)

# Create async engine
async_engine = create_async_engine(settings.database_url, echo=False)


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    # Import models to register them
    from src.models.db import File, Page, PageImage  # noqa: F401

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    logger.info(f"Database initialized at: {settings.database_url}")


def get_async_db_session():
    """Get an async database session context manager."""
    return AsyncSession(async_engine)
