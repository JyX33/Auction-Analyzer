"""
Database operations for managing item data.
"""

import logging
from typing import List, Optional, Dict, Any, AsyncIterator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from sqlalchemy.sql.expression import bindparam

from .models import Item, Group, ItemGroup
from .init_db import get_engine

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Async context manager for database sessions"""
    engine = await get_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Session rollback due to error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_item_by_id(session: AsyncSession, item_id: int) -> Optional[Item]:
    """Retrieve an item by its ID."""
    try:
        result = await session.execute(select(Item).where(Item.item_id == item_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Failed to get item {item_id}: {str(e)}")
        raise

async def create_item(session: AsyncSession, item_data: Dict[str, Any]) -> Item:
    """Create a new item or update if exists."""
    try:
        stmt = (
            sqlite_upsert(Item)
            .values(item_data)
            .on_conflict_do_update(
                index_elements=[Item.item_id],
                set_=item_data
            )
        )
        await session.execute(stmt)
        await session.commit()
        return await get_item_by_id(session, item_data['item_id'])
    except SQLAlchemyError as e:
        logger.error(f"Failed to create/update item: {str(e)}")
        await session.rollback()
        raise

async def get_items(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Item]:
    """Optimized item query with filtering and pagination"""
    try:
        query = select(Item)
        
        if filters:
            if "item_class_id" in filters:
                query = query.where(Item.item_class_id == filters["item_class_id"])
            if "item_subclass_id" in filters:
                query = query.where(Item.item_subclass_id == filters["item_subclass_id"])
            if "item_class_name" in filters:
                query = query.where(Item.item_class_name == filters["item_class_name"])
            if "item_subclass_name" in filters:
                query = query.where(Item.item_subclass_name == filters["item_subclass_name"])
            if "group_id" in filters:
                query = query.join(ItemGroup).where(ItemGroup.group_id == filters["group_id"])
        
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Query failed: {str(e)}")
        raise

async def create_group(session: AsyncSession, group_name: str) -> Group:
    """Create a new group."""
    group = Group(group_name=group_name)
    session.add(group)
    await session.commit()
    return group

async def add_item_to_group(
    session: AsyncSession,
    item_id: int,
    group_id: int
) -> Optional[ItemGroup]:
    """Add an item to a group."""
    item_group = ItemGroup(item_id=item_id, group_id=group_id)
    session.add(item_group)
    try:
        await session.commit()
        return item_group
    except IntegrityError:
        await session.rollback()
        return None

async def upsert_items(session: AsyncSession, items: List[dict]):
    """Batch upsert items with optimized conflict handling"""
    try:
        stmt = (
            sqlite_upsert(Item)
            .values(items)
            .on_conflict_do_update(
                index_elements=[Item.item_id],
                set_={
                    "item_class_id": bindparam("item_class_id"),
                    "item_class_name": bindparam("item_class_name"),
                    "item_subclass_id": bindparam("item_subclass_id"),
                    "item_subclass_name": bindparam("item_subclass_name"),
                    "display_subclass_name": bindparam("display_subclass_name"),
                    "item_name": bindparam("item_name")
                }
            )
        )
        
        # Execute in batches without explicit commit
        batch_size = 1000
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            await session.execute(stmt, batch)
            
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Batch upsert failed: {str(e)}")
        raise RuntimeError(f"Database error: {str(e)}") from e

async def item_exists(session: AsyncSession, item_id: int) -> bool:
    """Check if an item exists in the database"""
    result = await session.execute(
        select(exists().where(Item.item_id == item_id))
    )
    return result.scalar()
