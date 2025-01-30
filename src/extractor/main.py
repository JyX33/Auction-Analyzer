# src/extractor/main.py
import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.operations import (
    connected_realm_exists,
    get_all_item_ids,
    get_connected_realm_by_id,
    get_session,
    upsert_auctions,
    upsert_connected_realm,
    upsert_items,
)

from .api_client import BlizzardAPIClient


class ItemExtractor:
    def __init__(self):
        self.client = BlizzardAPIClient(
            os.getenv("BLIZZARD_CLIENT_ID"), os.getenv("BLIZZARD_CLIENT_SECRET")
        )
        self.stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "retries": 0,
            "realms_processed": 0,
            "realms_succeeded": 0,
            "realms_failed": 0,
            "realms_skipped": 0,  # Realms already in DB
            "items_skipped": 0,  # Items already in DB
            "auctions_processed": 0,  # New auction stats
            "auctions_succeeded": 0,
            "auctions_failed": 0,
            "auctions_skipped": 0,  # Auctions already in DB and unchanged
        }

    def transform_item(self, raw_data: dict) -> dict:
        """Transform API response to database schema"""
        if not raw_data.get("results") or not raw_data["results"]:
            raise ValueError("No results found in API response")

        item = raw_data["results"][0]["data"]
        try:
            return {
                "item_id": item["id"],
                "item_name": item[
                    "name"
                ],  # Direct API returns string, not localized dict
                "item_class_id": item["item_class"]["id"],
                "item_class_name": item["item_class"]["name"],  # Direct string
                "item_subclass_id": item["item_subclass"]["id"],
                "item_subclass_name": item["item_subclass"]["name"],  # Direct string
                "display_subclass_name": "",  # Not available in direct API
            }
        except (KeyError, IndexError) as e:
            logging.error(f"Failed to transform item data: {str(e)}")
            logging.debug(f"Raw data: {raw_data}")
            raise ValueError(f"Invalid item data structure: {str(e)}")

    async def extract_connected_realms(self, session: AsyncSession):
        """Extract and store connected realm data"""
        try:
            realm_ids = await self.client.fetch_connected_realms_index()
            for realm_id in realm_ids:
                try:
                    self.stats["realms_processed"] += 1

                    # Check if realm already exists and skip if it does
                    if await connected_realm_exists(session, realm_id):
                        logging.debug(f"Skipping existing connected realm {realm_id}")
                        self.stats["realms_skipped"] += 1
                        continue

                    realm_data = await self.client.fetch_connected_realm_details(
                        realm_id
                    )
                    if realm_data:
                        realm_data["last_updated"] = datetime.utcnow()
                        await upsert_connected_realm(session, realm_data)
                        self.stats["realms_succeeded"] += 1
                    else:
                        self.stats["realms_failed"] += 1
                except Exception as e:
                    self.stats["realms_failed"] += 1
                    logging.error(f"Failed to process realm {realm_id}: {str(e)}")
            return True
        except Exception as e:
            logging.error(f"Connected realms extraction failed: {str(e)}")
            return False

    async def process_realm_auctions(
        self, session: AsyncSession, connected_realm_id: int
    ):
        """Process auctions for a single realm with error handling"""
        logging.info(f"Starting auction processing for realm {connected_realm_id}")
        start_time = time.perf_counter()

        try:
            # Get realm details using provided session
            realm = await get_connected_realm_by_id(session, connected_realm_id)
            if not realm:
                logging.error(
                    f"Connected realm {connected_realm_id} not found in database"
                )
                return False

            # Get current item IDs
            item_ids = await get_all_item_ids(session)

            # Fetch auctions
            auctions = await self.client.fetch_auctions(connected_realm_id, item_ids)
            if not auctions:
                logging.info(f"No auctions found for realm {connected_realm_id}")
                return True

            # Process auctions with the same session
            batch_size = 5000  # Increased batch size
            for i in range(0, len(auctions), batch_size):
                batch = auctions[i: i + batch_size]
                try:
                    self.stats["auctions_processed"] += len(batch)
                    await upsert_auctions(batch)
                    self.stats["auctions_succeeded"] += len(batch)
                except Exception as e:
                    self.stats["auctions_failed"] += len(batch)
                    logging.error(f"Failed to process auction batch: {str(e)}")

            processing_time = time.perf_counter() - start_time
            logging.info(
                f"Completed processing {len(auctions)} auctions for realm {connected_realm_id} "
                f"in {processing_time:.2f} seconds"
            )
            return True

        except Exception as e:
            logging.error(
                f"Auction extraction failed for realm {connected_realm_id}: {str(e)}"
            )
            return False

    async def extract_auctions(self, session: AsyncSession, connected_realm_id: int):
        """Extract and store auction data for a connected realm"""
        return await self.process_realm_auctions(session, connected_realm_id)

    async def process_batch(self, item_ids: List[int]):
        """Process batch of items with dedicated session"""
        try:
            async with get_session() as session:
                # Get all existing item IDs from the database
                existing_items = await get_all_item_ids(session)

                # Filter out existing items efficiently using set operations
                items_to_process = [
                    item_id for item_id in item_ids if item_id not in existing_items
                ]
                skipped_items = [
                    item_id for item_id in item_ids if item_id in existing_items
                ]

                # Update stats for skipped items
                for item_id in skipped_items:
                    logging.debug(f"Skipping existing item {item_id}")
                    self.stats["items_skipped"] += 1

                if not items_to_process:
                    logging.info("All items in batch already exist, skipping batch")
                    return True

                tasks = [
                    self.process_single_item(item_id, session)
                    for item_id in items_to_process
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Handle failed items
                failed_items = [
                    item_id
                    for item_id, result in zip(items_to_process, results)
                    if isinstance(result, Exception)
                ]

                if failed_items:
                    logging.info(f"Retrying {len(failed_items)} failed items")
                    retry_results = await asyncio.gather(
                        *[
                            self.process_single_item(item_id, session)
                            for item_id in failed_items
                        ],
                        return_exceptions=True,
                    )
                    # Update stats based on retry results
                    self.stats["succeeded"] += sum(
                        1 for res in retry_results if not isinstance(res, Exception)
                    )
                    self.stats["failed"] += sum(
                        1 for res in retry_results if isinstance(res, Exception)
                    )
                return True
        except Exception as e:
            logging.error(f"Batch processing failed: {str(e)}")
            return False

    async def process_single_item(self, item_id: int, session: AsyncSession):
        """Process item with proper session management"""
        self.stats["processed"] += 1
        try:
            raw_data = await self.client.fetch_item(item_id)
            item_data = self.transform_item(raw_data)
            await upsert_items(session, [item_data])
            self.stats["succeeded"] += 1
            return item_id
        except Exception as e:
            self.stats["failed"] += 1
            logging.error(f"Item {item_id} error: {str(e)}")
            raise

    def generate_report(self):
        """Generate extraction report in output/ directory"""
        report_dir = Path("output")
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%d-%m-%Y-%H%M%S")
        report_path = report_dir / f"extraction_report_{timestamp}.md"

        report_content = f"""# Extraction Report - {timestamp}
        
## Item Summary
- Total Items Processed: {self.stats['processed']}
- Successful: {self.stats['succeeded']}
- Failed: {self.stats['failed']}
- Skipped (Already Exist): {self.stats['items_skipped']}
- Retry Attempts: {self.stats['retries']}

## Connected Realms Summary
- Total Realms Processed: {self.stats['realms_processed']}
- Successful: {self.stats['realms_succeeded']}
- Failed: {self.stats['realms_failed']}
- Skipped (Already Exist): {self.stats['realms_skipped']}

## Auction Summary
- Total Auctions Processed: {self.stats['auctions_processed']}
- Successful: {self.stats['auctions_succeeded']}
- Failed: {self.stats['auctions_failed']}
- Skipped (Already Exist): {self.stats['auctions_skipped']}
        """

        with open(report_path, "w") as f:
            f.write(report_content)


async def main(item_ids: List[int]):
    """Main entry point with proper transaction handling"""
    extractor = ItemExtractor()

    try:
        # Create API client session first
        async with extractor.client.session():
            # Process operations with dedicated sessions
            logging.info("Extracting connected realms data...")
            async with get_session() as session:
                realms_success = await extractor.extract_connected_realms(session)

            if not realms_success:
                logging.error("Connected realms extraction failed")
                return False

            # Process items in batches with delay
            logging.info("Processing items...")
            batch_size = 50
            for i in range(0, len(item_ids), batch_size):
                batch = item_ids[i: i + batch_size]
                await extractor.process_batch(batch)
                if i + batch_size < len(item_ids):  # Don't delay after last batch
                    await asyncio.sleep(1)  # 1000ms = 1s

            # Extract auctions for all connected realms in parallel
            logging.info("Extracting auction data...")
            realm_ids = await extractor.client.fetch_connected_realms_index()

            # Create semaphore to limit concurrent realm processing
            realm_semaphore = asyncio.Semaphore(10)  # Process 10 realms at a time

            async def process_realm_with_session(realm_id: int) -> bool:
                async with realm_semaphore:  # Limit concurrent processing
                    async with get_session() as session:  # Each realm gets its own session
                        return await extractor.extract_auctions(session, realm_id)

            # Create tasks for all realms with individual sessions
            start_time = time.perf_counter()
            realm_tasks = [
                process_realm_with_session(realm_id) for realm_id in realm_ids
            ]
            results = await asyncio.gather(*realm_tasks, return_exceptions=True)
            processing_time = time.perf_counter() - start_time

            # Handle results and any exceptions
            failed_realms = [
                realm_id
                for realm_id, result in zip(realm_ids, results)
                if isinstance(result, Exception) or result is False
            ]

            if failed_realms:
                logging.error(f"Failed to process realms: {failed_realms}")

            total_realms = len(realm_ids)
            successful_realms = total_realms - len(failed_realms)
            logging.info(
                f"Completed auction extraction for {successful_realms}/{total_realms} realms "
                f"in {processing_time:.2f} seconds"
            )

            extractor.generate_report()
            return len(failed_realms) == 0
    except Exception as e:
        logging.critical(f"Extraction aborted: {str(e)}")
        extractor.generate_report()
        return False
