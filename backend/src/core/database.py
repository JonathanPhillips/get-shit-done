"""Database configuration and session management."""
import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.core.config import settings

logger = logging.getLogger(__name__)

# Log database configuration for debugging
logger.info(f"Database URL: {settings.database_url}")
db_path = settings.database_url.replace("sqlite+aiosqlite://", "")
if os.path.exists(os.path.dirname(db_path)):
    logger.info(f"Database directory exists: {os.path.dirname(db_path)}")
    logger.info(f"Directory permissions: {oct(os.stat(os.path.dirname(db_path)).st_mode)}")
else:
    logger.warning(f"Database directory does not exist: {os.path.dirname(db_path)}")

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    connect_args={"check_same_thread": False},
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables."""
    try:
        logger.info("Initializing database...")
        # Import models to register them with Base
        from src.models import Task, PomodoroSession  # noqa: F401
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise


async def close_db():
    """Close database connections."""
    await engine.dispose()
