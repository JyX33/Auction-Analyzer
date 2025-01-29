# src/extractor/main.py
import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.operations import upsert_items

from .rate_limiter import RateLimiter


class ItemExtractor:
    def __init__(self):
        self.client_id = os.getenv("BLIZZARD_CLIENT_ID")
        self.client_secret = os.getenv("BLIZZARD_CLIENT_SECRET")
        self.access_token = None
        self.rate_limiter = RateLimiter()
        self.base_url = "https://eu.api.blizzard.com/data/wow"
        self.stats = {"processed": 0, "succeeded": 0, "failed": 0, "retries": 0}

    async def authenticate(self):
        """Obtain OAuth token from Blizzard API"""
        auth_url = "https://oauth.battle.net/token"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_url,
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
            )
            response.raise_for_status()
            self.access_token = response.json()["access_token"]

    async def fetch_item(self, client: httpx.AsyncClient, item_id: int) -> dict:
        """Fetch item data from Blizzard API"""
        url = f"{self.base_url}/search/item?id={item_id}"
        response = await self.rate_limiter.execute_with_retry(
            client.get(url, headers={"Authorization": f"Bearer {self.access_token}"})
        )
        response.raise_for_status()
        return response.json()

    def transform_item(self, raw_data: dict) -> dict:
        """Transform API response to database schema"""
        item = raw_data["results"][0]["data"]
        return {
            "item_id": item["id"],
            "item_name": item["name"]["en_US"],
            "item_class_id": item["item_class"]["id"],
            "item_class_name": item["item_class"]["name"],
            "item_subclass_id": item["item_subclass"]["id"],
            "item_subclass_name": item["item_subclass"]["name"],
            "display_subclass_name": item["item_subclass"].get("display_name", ""),
        }

    async def process_batch(self, session: AsyncSession, item_ids: List[int]):
        """Process batch with detailed error tracking and retries"""
        failed_items = []
        async with httpx.AsyncClient() as client:
            results = await asyncio.gather(
                *[self.process_single_item(client, item_id, session) 
                  for item_id in item_ids],
                return_exceptions=True
            )
            
            # Process results and collect failures
            for item_id, result in zip(item_ids, results):
                if isinstance(result, Exception):
                    logging.warning(f"Failed item {item_id}: {str(result)}")
                    failed_items.append(item_id)
                    self.stats["retries"] += 1

        # Retry failed items once
        if failed_items:
            logging.info(f"Retrying {len(failed_items)} failed items")
            async with httpx.AsyncClient() as client:
                await asyncio.gather(
                    *[self.process_single_item(client, item_id, session)
                      for item_id in failed_items]
                )

    async def process_single_item(
        self, client: httpx.AsyncClient, item_id: int, session: AsyncSession
    ):
        """Process item with transaction management"""
        self.stats["processed"] += 1
        try:
            async with session.begin_nested():  # Use nested transaction
                raw_data = await self.fetch_item(client, item_id)
                item_data = self.transform_item(raw_data)
                await upsert_items(session, [item_data])
                self.stats["succeeded"] += 1
                return item_id
        except Exception as e:
            self.stats["failed"] += 1
            logging.error(f"Item {item_id} error: {str(e)}")
            raise  # Re-raise to be caught in process_batch

    def generate_report(self):
        """Generate extraction report in output/ directory"""
        report_dir = Path("output")
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%d-%m-%Y-%H%M%S")
        report_path = report_dir / f"extraction_report_{timestamp}.md"

        report_content = f"""# Extraction Report - {timestamp}
        
        ## Summary
        - Total Items Processed: {self.stats['processed']}
        - Successful: {self.stats['succeeded']}
        - Failed: {self.stats['failed']}
        - Retry Attempts: {self.stats['retries']}
        """

        with open(report_path, "w") as f:
            f.write(report_content)


async def main(item_ids: List[int], session: AsyncSession):
    """Main entry point with proper transaction handling"""
    extractor = ItemExtractor()
    await extractor.authenticate()

    try:
        async with session.begin():  # Single transaction for all batches
            batch_size = 100
            for i in range(0, len(item_ids), batch_size):
                batch = item_ids[i:i + batch_size]
                await extractor.process_batch(session, batch)

        extractor.generate_report()
        return True
    except Exception as e:
        await session.rollback()
        logging.critical(f"Extraction aborted: {str(e)}")
        extractor.generate_report()
        return False
