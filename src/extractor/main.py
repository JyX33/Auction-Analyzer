import asyncio
import httpx
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from .rate_limiter import RateLimiter
from src.database.operations import upsert_items
from src.database.models import Item

class ItemExtractor:
    def __init__(self):
        self.client_id = os.getenv("BLIZZARD_CLIENT_ID")
        self.client_secret = os.getenv("BLIZZARD_CLIENT_SECRET")
        self.access_token = None
        self.rate_limiter = RateLimiter()
        self.base_url = "https://us.api.blizzard.com/data/wow"
        self.stats = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "retries": 0
        }

    async def authenticate(self):
        """Obtain OAuth token from Blizzard API"""
        auth_url = "https://oauth.battle.net/token"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_url,
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"}
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
            "display_subclass_name": item["item_subclass"].get("display_name", "")
        }

    async def process_batch(self, session: AsyncSession, item_ids: List[int]):
        """Process a batch of item IDs"""
        async with httpx.AsyncClient() as client:
            tasks = [self.process_single_item(client, item_id, session) 
                    for item_id in item_ids]
            await asyncio.gather(*tasks)

    async def process_single_item(self, client: httpx.AsyncClient, item_id: int, session: AsyncSession):
        """Process individual item with error handling"""
        self.stats["processed"] += 1
        try:
            raw_data = await self.fetch_item(client, item_id)
            item_data = self.transform_item(raw_data)
            await upsert_items(session, [item_data])
            self.stats["succeeded"] += 1
        except Exception as e:
            self.stats["failed"] += 1
            logging.error(f"Failed to process item {item_id}: {str(e)}")

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
    """Main entry point for the extraction process"""
    extractor = ItemExtractor()
    await extractor.authenticate()
    
    try:
        batch_size = 100
        for i in range(0, len(item_ids), batch_size):
            batch = item_ids[i:i+batch_size]
            await extractor.process_batch(session, batch)
            
        extractor.generate_report()
        return True
    except Exception as e:
        logging.error(f"Fatal error during extraction: {str(e)}")
        return False
