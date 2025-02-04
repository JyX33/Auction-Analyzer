"""Script to update realm population data for multiple realms"""
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


def load_population_data():
    with open(project_root / "realm_characters.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for entry in data:
        names = entry["realm_name"].split(',')
        for name in names:
            normalized = name.strip().lower().replace("'", "").replace("/", "-")
            mapping[normalized] = entry["characters_number"]
    return mapping

POPULATION_DATA = load_population_data()

async def update_realm_populations():
    async with get_session() as session:
        # Fetch all realms
        stmt = select(ConnectedRealm)
        result = await session.execute(stmt)
        realms = result.scalars().all()
        
        updates = 0
        print("Updating realm populations...")
        
        for realm in realms:
            # Normalize realm name to match dictionary keys
            realm_name = realm.name.lower().replace("'", "").replace("/", "-")
            if realm_name in POPULATION_DATA:
                realm.population = POPULATION_DATA[realm_name]
                realm.last_updated = datetime.utcnow()
                updates += 1
                print(f"Updated {realm.name} with population {realm.population}")
        
        if updates > 0:
            await session.commit()
            print(f"\nSuccessfully updated {updates} realms")
        else:
            print("\nNo matching realms found to update")

if __name__ == "__main__":
    asyncio.run(update_realm_populations())
