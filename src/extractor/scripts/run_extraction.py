import asyncio
import logging
import os
from pathlib import Path
from typing import List

from src.database.init_db import initialize_database
from src.extractor.main import main as run_extraction

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def read_item_ids(file_path: str = "items.txt") -> List[tuple]:
    """Read and parse item IDs with extensions from a text file"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Item ID file not found: {path.resolve()}")

    items = []
    current_extension = None
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Handle extension declarations
            if line.lower().startswith("extension="):
                current_extension = line.split("=", 1)[1].strip() or None
                continue

            # Handle item IDs with current extension
            for id_str in line.split(","):
                id_str = id_str.strip()
                if id_str.isdigit():
                    items.append((int(id_str), current_extension))

    if not items:
        raise ValueError("No valid item IDs found in the input file")

    logger.info(f"Loaded {len(items)} items with extensions from {path.name}")
    return items


async def extraction_wrapper():
    """Wrapper function for the extraction process"""
    # Check required environment variables
    if not all(
        os.getenv(var) for var in ["BLIZZARD_CLIENT_ID", "BLIZZARD_CLIENT_SECRET"]
    ):
        raise RuntimeError("Missing Blizzard API credentials in environment variables")

    # Initialize database
    await initialize_database()

    # Read items with extensions
    item_entries = read_item_ids()

    # Run extraction with (id, extension) tuples

    success = await run_extraction(item_entries)

    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(extraction_wrapper())
        exit_code = 0 if result else 1
    except Exception as e:
        logger.critical(f"Extraction failed: {str(e)}")
        exit_code = 1

    exit(exit_code)
