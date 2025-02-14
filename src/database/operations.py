"""
Database operations for managing item data.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, AsyncIterator, Dict, List, Optional

from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import bindparam

from .init_db import get_engine, get_sync_engine
from .models import Auction, Commodity, ConnectedRealm, Group, Item, ItemGroup

# Batch size for auction processing
AUCTION_BATCH_SIZE = 2000
COMMODITY_BATCH_SIZE = 1000
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

logger = logging.getLogger(__name__)


def get_db():
    """Synchronous database session for FastAPI dependency injection"""
    engine = get_sync_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Async context manager for database sessions with concurrency control"""
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
            .on_conflict_do_update(index_elements=[Item.item_id], set_=item_data)
        )
        await session.execute(stmt)
        await session.commit()
        return await get_item_by_id(session, item_data["item_id"])
    except SQLAlchemyError as e:
        logger.error(f"Failed to create/update item: {str(e)}")
        await session.rollback()
        raise


async def get_items(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 100,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Item]:
    """Optimized item query with filtering and pagination"""
    try:
        query = select(Item)

        if filters:
            if "item_class_id" in filters:
                query = query.where(Item.item_class_id == filters["item_class_id"])
            if "item_subclass_id" in filters:
                query = query.where(
                    Item.item_subclass_id == filters["item_subclass_id"]
                )
            if "item_class_name" in filters:
                query = query.where(Item.item_class_name == filters["item_class_name"])
            if "item_subclass_name" in filters:
                query = query.where(
                    Item.item_subclass_name == filters["item_subclass_name"]
                )
            if "group_id" in filters:
                query = query.join(ItemGroup).where(
                    ItemGroup.group_id == filters["group_id"]
                )

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
    session: AsyncSession, item_id: int, group_id: int
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
    """Batch upsert items"""
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
                "item_name": bindparam("item_name"),
                "extension": bindparam("extension"),
            },
        )
    )
    await session.execute(stmt, items)


async def item_exists(session: AsyncSession, item_id: int) -> bool:
    """Check if an item exists in the database"""
    result = await session.execute(select(exists().where(Item.item_id == item_id)))
    return result.scalar()


async def get_connected_realm_by_id(
    session: AsyncSession, connected_realm_id: int
) -> Optional[ConnectedRealm]:
    """Retrieve a connected realm by its ID."""
    try:
        result = await session.execute(
            select(ConnectedRealm).where(
                ConnectedRealm.connected_realm_id == connected_realm_id
            )
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Failed to get connected realm {connected_realm_id}: {str(e)}")
        raise


async def upsert_connected_realm(
    session: AsyncSession, realm_data: Dict[str, Any]
) -> ConnectedRealm:
    """Create or update a connected realm."""
    try:
        stmt = (
            sqlite_upsert(ConnectedRealm)
            .values(realm_data)
            .on_conflict_do_update(
                index_elements=[ConnectedRealm.connected_realm_id],
                set_={
                    "name": bindparam("_name", value=realm_data["name"]),
                    "population_type": bindparam(
                        "_population_type", value=realm_data["population_type"]
                    ),
                    "realm_category": bindparam(
                        "_realm_category", value=realm_data["realm_category"]
                    ),
                    "status": bindparam("_status", value=realm_data["status"]),
                    "population": bindparam(
                        "_population", value=realm_data.get("population")
                    ),
                    "last_updated": bindparam(
                        "_last_updated", value=realm_data["last_updated"]
                    ),
                },
            )
        )
        await session.execute(stmt)
        await session.commit()
        return await get_connected_realm_by_id(
            session, realm_data["connected_realm_id"]
        )
    except SQLAlchemyError as e:
        logger.error(f"Failed to create/update connected realm: {str(e)}")
        await session.rollback()
        raise


async def get_connected_realms(
    session: AsyncSession, page: int = 1, page_size: int = 100
) -> List[ConnectedRealm]:
    """Get all connected realms with pagination."""
    try:
        query = select(ConnectedRealm).offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Failed to get connected realms: {str(e)}")
        raise


async def get_all_item_ids(session: AsyncSession) -> set[int]:
    """Get all item IDs from the database."""
    result = await session.execute(select(Item.item_id))
    return set(row[0] for row in result.all())


async def connected_realm_exists(
    session: AsyncSession, connected_realm_id: int
) -> bool:
    """Check if a connected realm exists in the database."""
    result = await session.execute(
        select(exists().where(ConnectedRealm.connected_realm_id == connected_realm_id))
    )
    return result.scalar()


async def auction_exists(
    session: AsyncSession, auction_id: int, connected_realm_id: int
) -> bool:
    """Check if an auction exists in the database."""
    result = await session.execute(
        select(
            exists().where(
                (Auction.auction_id == auction_id)
                & (Auction.connected_realm_id == connected_realm_id)
            )
        )
    )
    return result.scalar()


async def process_auction_batch(batch: List[dict]):
    """Process a batch of auctions."""
    if not batch:
        return

    async with get_session() as session:
        try:
            stmt = (
                sqlite_upsert(Auction)
                .values(batch)
                .on_conflict_do_update(
                    index_elements=[Auction.auction_id, Auction.connected_realm_id],
                    set_=dict(
                        item_id=Auction.item_id,
                        buyout_price=Auction.buyout_price,
                        quantity=Auction.quantity,
                        time_left=Auction.time_left,
                        last_modified=Auction.last_modified,
                        active=Auction.active,
                    ),
                )
            )
            await session.execute(stmt)
            await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Failed to upsert auction batch: {str(e)}")
            await session.rollback()
            raise


async def upsert_auctions(auctions: List[dict]):
    """Batch upsert auctions with optimized parallel processing."""
    if not auctions:
        return

    # Ensure all auctions have active flag set
    for auction in auctions:
        if "active" not in auction:
            auction["active"] = True

    # Process auctions in batches
    batches = [
        auctions[i:i + AUCTION_BATCH_SIZE]
        for i in range(0, len(auctions), AUCTION_BATCH_SIZE)
    ]
    logger.info(f"Processing {len(auctions)} auctions in {len(batches)} batches")
    processing_start = time.perf_counter()

    try:
        # Process batches in parallel with controlled concurrency
        tasks = [process_auction_batch(batch) for batch in batches]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Failed to process auction batches: {str(e)}")
        raise

    # Calculate and log processing metrics
    processing_time = time.perf_counter() - processing_start
    logger.info(
        f"Processed {len(auctions)} auctions in {processing_time:.2f} seconds "
        f"({len(auctions) / processing_time:.2f} auctions/second)"
    )


async def get_auctions(
    session: AsyncSession,
    connected_realm_id: Optional[int] = None,
    item_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 100,
) -> List[Auction]:
    """Get auctions with optional filtering and pagination."""
    try:
        query = select(Auction).where(Auction.active)  # Only get active auctions

        if connected_realm_id is not None:
            query = query.where(Auction.connected_realm_id == connected_realm_id)
        if item_id is not None:
            query = query.where(Auction.item_id == item_id)

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Failed to get auctions: {str(e)}")
        raise


async def delete_old_auctions(days: int = 7) -> int:
    """Delete auctions that are older than the specified number of days.

    Args:
        days: Number of days. Auctions older than this will be deleted.

    Returns:
        int: Number of auctions deleted
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    logger.info(f"Deleting auctions older than {cutoff_date}")

    try:
        async with get_session() as session:
            stmt = delete(Auction).where(Auction.last_modified < cutoff_date)
            result = await session.execute(stmt)
            deleted_count = result.rowcount
            await session.commit()

            logger.info(f"Successfully deleted {deleted_count} old auctions")
            return deleted_count

    except SQLAlchemyError as e:
        logger.error(f"Failed to delete old auctions: {str(e)}")
        raise


async def process_commodity_batch(batch: List[dict]):
    """Process a batch of commodities with quantity merging for same item_id and unit_price."""
    if not batch:
        return

    # Group commodities by item_id and unit_price, summing quantities
    merged_commodities = {}
    for commodity in batch:
        key = (commodity["item_id"], commodity["unit_price"])
        if key in merged_commodities:
            merged_commodities[key]["quantity"] += commodity["quantity"]
        else:
            merged_commodities[key] = commodity

    retries = 0
    while retries < MAX_RETRIES:
        try:
            async with get_session() as session:
                stmt = (
                    sqlite_upsert(Commodity)
                    .values(list(merged_commodities.values()))
                    .on_conflict_do_update(
                        index_elements=[Commodity.item_id, Commodity.unit_price],
                        set_=dict(
                            quantity=Commodity.quantity,
                            last_modified=Commodity.last_modified,
                        ),
                    )
                )
                await session.execute(stmt)
                await session.commit()
                break  # Success, exit retry loop
        except OperationalError as e:
            if "database is locked" in str(e) and retries < MAX_RETRIES - 1:
                retries += 1
                logger.warning(
                    f"Database locked, retrying in {RETRY_DELAY} seconds (attempt {retries}/{MAX_RETRIES})"
                )
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to upsert commodity batch after {MAX_RETRIES} attempts: {str(e)}")
                raise
        except SQLAlchemyError as e:
            logger.error(f"Failed to upsert commodity batch: {str(e)}")
            raise


async def upsert_commodities(commodities: List[dict]):
    """Batch upsert commodities with quantity merging."""
    if not commodities:
        return

    # Process commodities in batches
    batches = [
        commodities[i:i + COMMODITY_BATCH_SIZE]
        for i in range(0, len(commodities), COMMODITY_BATCH_SIZE)
    ]
    logger.info(f"Processing {len(commodities)} commodities in {len(batches)} batches")
    processing_start = time.perf_counter()

    try:
        tasks = [process_commodity_batch(batch) for batch in batches]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Failed to process commodity batches: {str(e)}")
        raise

    processing_time = time.perf_counter() - processing_start
    logger.info(
        f"Processed {len(commodities)} commodities in {processing_time:.2f} seconds "
        f"({len(commodities) / processing_time:.2f} commodities/second)"
    )


async def delete_all_commodities() -> int:
    """Delete all commodities from the database.

    Returns:
        int: Number of commodities deleted
    """
    try:
        async with get_session() as session:
            stmt = delete(Commodity)
            result = await session.execute(stmt)
            deleted_count = result.rowcount
            await session.commit()

            logger.info(f"Successfully deleted {deleted_count} commodities")
            return deleted_count

    except SQLAlchemyError as e:
        logger.error(f"Failed to delete commodities: {str(e)}")
        raise
