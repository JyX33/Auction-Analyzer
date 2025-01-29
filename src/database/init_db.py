# src/database/init_db.py
"""Database initialization and migration configuration."""
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy_utils import database_exists, create_database
from src.database.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./items.db")

async def get_engine() -> AsyncEngine:
    """Create and return async database engine."""
    return create_async_engine(
        DATABASE_URL,
        echo=True,  # SQL query logging
        future=True
    )

async def initialize_database():
    """Initialize database with async support."""
    # Create database if it doesn't exist (using sync engine temporarily)
    sync_url = DATABASE_URL.replace("+aiosqlite", "")
    if not database_exists(sync_url):
        create_database(sync_url)
        logging.info(f"Created database at {sync_url}")

    # Initialize schema using async engine
    engine = await get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logging.info("Database schema created successfully")

    await engine.dispose()
    logging.info("Database initialization complete")

if __name__ == "__main__":
    import asyncio
    asyncio.run(initialize_database())
