"""Script to update realm logs data from realm_logs.json"""
# flake8: noqa: E402
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[3]  # noqa: E402
sys.path.insert(0, str(project_root))  # noqa: E402
import asyncio
import json
from datetime import datetime
from sqlalchemy import select
from src.database.models import ConnectedRealm
from src.database.operations import get_session


def load_logs_data():
    """Load and parse realm logs data from the JSON file, converting to integers."""
    with open(project_root / "realm_logs.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    mapping = {}
    for entry in data["realm_data"]:
        # Normalize realm name by converting to lowercase and removing special characters
        normalized_name = entry["realm_name"].lower().replace("'", "").replace(" ", "-")
        # Convert logs value to integer (remove commas from formatted numbers)
        try:
            # Remove commas from the number string before converting to int
            logs_str = str(entry["logs"]).replace(",", "")
            logs_value = int(logs_str)
        except (ValueError, TypeError):
            print(f"Warning: Invalid logs value for {entry['realm_name']}: {entry['logs']}, using 0")
            logs_value = 0
        mapping[normalized_name] = logs_value
    return mapping


async def update_realm_logs():
    """Update the logs field for each realm in the database."""
    # Load the logs data from JSON
    LOGS_DATA = load_logs_data()
    
    async with get_session() as session:
        # Fetch all realms
        stmt = select(ConnectedRealm)
        result = await session.execute(stmt)
        realms = result.scalars().all()
        
        updates = 0
        print("Updating realm logs data...")
        
        for realm in realms:
            # Normalize realm name to match dictionary keys
            realm_name = realm.name.lower().replace("'", "").replace(" ", "-")
            if realm_name in LOGS_DATA:
                realm.logs = LOGS_DATA[realm_name]
                realm.last_updated = datetime.utcnow()
                updates += 1
                print(f"Updated {realm.name} with logs count: {realm.logs}")
        
        if updates > 0:
            await session.commit()
            print(f"\nSuccessfully updated {updates} realms")
        else:
            print("\nNo matching realms found to update")


if __name__ == "__main__":
    asyncio.run(update_realm_logs())