"""
Database operations for managing item data.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, exists
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .models import Item, Group, ItemGroup

async def get_item_by_id(session: AsyncSession, item_id: int) -> Optional[Item]:
    """Retrieve an item by its ID."""
    result = await session.execute(select(Item).where(Item.item_id == item_id))
    return result.scalar_one_or_none()

async def create_item(session: AsyncSession, item_data: Dict[str, Any]) -> Item:
    """Create a new item or update if exists."""
    item = Item(**item_data)
    try:
        session.add(item)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        existing = await get_item_by_id(session, item_data['item_id'])
        if existing:
            for key, value in item_data.items():
                setattr(existing, key, value)
            await session.commit()
            return existing
    return item

async def get_items(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 15,
    item_class_name: Optional[str] = None,
    item_subclass_name: Optional[str] = None
) -> List[Item]:
    """Retrieve items with optional filtering and pagination."""
    query = select(Item)
    
    if item_class_name:
        query = query.where(Item.item_class_name == item_class_name)
    if item_subclass_name:
        query = query.where(Item.item_subclass_name == item_subclass_name)
    
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    return result.scalars().all()

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

async def upsert_items(session: AsyncSession, items: list[dict]):
    """Batch upsert items with conflict handling"""
    try:
        for item_data in items:
            stmt = select(Item).where(Item.item_id == item_data["item_id"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing item
                for key, value in item_data.items():
                    setattr(existing, key, value)
            else:
                # Insert new item
                session.add(Item(**item_data))
        
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        raise RuntimeError(f"Database error: {str(e)}") from e

async def item_exists(session: AsyncSession, item_id: int) -> bool:
    """Check if an item exists in the database"""
    result = await session.execute(
        select(exists().where(Item.item_id == item_id))
    )
    return result.scalar()
