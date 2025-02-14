# src/database/init_db.py
"""Database initialization and migration configuration."""
import logging
import os

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy_utils import create_database, database_exists

from src.database.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./items.db")
SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")

def _set_sqlite_pragma(dbapi_connection, _):
    """Set SQLite pragma statements for better concurrency."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # Enable Write-Ahead Logging
    cursor.execute("PRAGMA busy_timeout=30000")  # Set timeout to 30 seconds
    cursor.close()

def get_sync_engine():
    """Create and return synchronous database engine."""
    engine = create_engine(
        SYNC_DATABASE_URL,
        echo=False,  # SQL query logging
        future=True,
        connect_args={"timeout": 30},  # 30 second connection timeout
    )
    
    # Set SQLite pragmas after connection
    event.listen(engine, "connect", _set_sqlite_pragma)
    return engine

async def get_engine() -> AsyncEngine:
    """Create and return async database engine."""
    return create_async_engine(
        DATABASE_URL,
        echo=False,  # SQL query logging
        future=True,
        connect_args={"timeout": 30},  # 30 second connection timeout
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
        # Set SQLite pragmas using text()
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        await conn.execute(text("PRAGMA busy_timeout=30000"))
        logging.info("Database schema created successfully")

    await engine.dispose()
    logging.info("Database initialization complete")

def initialize_sync_database():
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
    import asyncio

    asyncio.run(initialize_database())
