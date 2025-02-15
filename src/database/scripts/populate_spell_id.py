#!/usr/bin/env python3

import csv
import logging
from pathlib import Path
from typing import Dict

from sqlalchemy.orm import Session, sessionmaker

from src.database.init_db import get_sync_engine
from src.database.models import Item

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_item_name(name: str) -> str:
    """
    Clean item name by removing profession prefixes and trimming whitespace.
    
    Args:
        name: Raw item name
        
    Returns:
        Cleaned item name
    """
    # List of profession prefixes to remove
    prefixes = [
        "Plans:", "Pattern:", "Design:", "Formula:", "Recipe:", 
        "Technique:", "Schematic:"
    ]
    
    # Remove any prefix if present
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):].strip()
            break
    
    return name

def load_spell_name_mapping(csv_path: str) -> Dict[str, int]:
    """
    Load the SpellName.csv file and create a mapping of spell names to IDs.
    
    Args:
        csv_path: Path to the SpellName CSV file
        
    Returns:
        Dictionary mapping spell names to their IDs
    """
    spell_mapping = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Assuming the CSV has 'ID' and 'Name_lang' columns
                spell_id = int(row['ID'])
                spell_name = row['Name_lang'].strip()
                if spell_name:  # Only add non-empty names
                    spell_mapping[spell_name] = spell_id
        
        logger.info(f"Loaded {len(spell_mapping)} spell names from CSV")
        return spell_mapping
    
    except FileNotFoundError:
        logger.error(f"SpellName CSV file not found at: {csv_path}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing CSV file: {e}")
        raise

def update_item_spell_ids(session: Session, spell_mapping: Dict[str, int]) -> None:
    """
    Update spell_id for items based on their names.
    
    Args:
        session: SQLAlchemy session
        spell_mapping: Dictionary mapping spell names to their IDs
    """
    try:
        items = session.query(Item).all()
        updated_count = 0
        not_found_count = 0
        
        for item in items:
            # Try to find spell ID using cleaned item name
            cleaned_name = clean_item_name(item.item_name)
            spell_id = spell_mapping.get(cleaned_name)
            
            if spell_id is not None:
                item.spell_id = spell_id
                updated_count += 1
                logger.debug(f"Found spell ID {spell_id} for item: {item.item_name}")
            else:
                not_found_count += 1
                logger.warning(f"No spell ID found for item: {item.item_name} (cleaned: {cleaned_name})")
        
        session.commit()
        logger.info(f"Updated {updated_count} items with spell IDs")
        logger.info(f"No spell ID found for {not_found_count} items")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating items: {e}")
        raise

def main() -> None:
    """Main function to populate spell IDs for items."""
    csv_path = str(Path(__file__).parents[3] / "wow_db_file" / "SpellName.11.1.0.59095.csv")
    
    try:
        # Load spell name mapping
        spell_mapping = load_spell_name_mapping(csv_path)
        
        # Create database session
        engine = get_sync_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Update items with spell IDs
            update_item_spell_ids(session, spell_mapping)
        finally:
            session.close()
            engine.dispose()
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()