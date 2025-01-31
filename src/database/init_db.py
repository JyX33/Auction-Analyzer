# src/database/init_db.py
"""Database initialization and migration configuration."""
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy_utils import create_database, database_exists

from src.database.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./items.db")
SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")


def get_sync_engine():
    """Create and return synchronous database engine."""
    return create_engine(
        SYNC_DATABASE_URL,
        echo=False,  # SQL query logging
        future=True
    )

async def get_engine() -> AsyncEngine:
    """Create and return async database engine."""
    return create_async_engine(
        DATABASE_URL, echo=False, future=True  # SQL query logging
    )


def initialize_database():
    """Initialize database with sync support."""
    # Create database if it doesn't exist
    if not database_exists(SYNC_DATABASE_URL):
        create_database(SYNC_DATABASE_URL)
        logging.info(f"Created database at {SYNC_DATABASE_URL}")

    # Initialize schema using sync engine
    engine = get_sync_engine()
    Base.metadata.create_all(engine)
    logging.info("Database schema created successfully")
    engine.dispose()
    logging.info("Database initialization complete")


if __name__ == "__main__":
    initialize_database()
