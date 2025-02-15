#!/usr/bin/env python3

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from sqlalchemy.orm import Session, sessionmaker

from src.database.init_db import get_sync_engine
from src.database.models import Item, Commodity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_reagent_name(name: str) -> str:
    """
    Fix specific reagent names that need to be adjusted.
    
    Args:
        name: Original reagent name
        
    Returns:
        Adjusted reagent name
    """
    name_mapping = {
        "Duskcloth Bolt": "Duskweave Bolt",
        "Dawncloth Bolt": "Dawnweave Bolt"
    }
    return name_mapping.get(name, name)

def load_item_sparse(csv_path: str) -> Dict[str, Set[int]]:
    """
    Load ItemSparse.csv and create a mapping from Display_lang to item IDs.
    
    Args:
        csv_path: Path to the ItemSparse CSV file
        
    Returns:
        Dictionary mapping Display_lang to sets of item IDs
    """
    name_to_ids = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                item_id = int(row['ID'])
                display_name = row['Display_lang'].strip()
                
                if display_name:  # Only map non-empty names
                    if display_name not in name_to_ids:
                        name_to_ids[display_name] = set()
                    name_to_ids[display_name].add(item_id)
        
        logger.info(f"Loaded {len(name_to_ids)} unique item names from ItemSparse CSV")
        return name_to_ids
    
    except FileNotFoundError:
        logger.error(f"ItemSparse CSV file not found at: {csv_path}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing ItemSparse CSV file: {e}")
        raise

def load_spell_reagents(csv_path: str) -> Dict[int, List[Tuple[int, int]]]:
    """
    Load SpellReagents.csv and create a mapping of spell IDs to their reagents.
    The CSV has columns Reagent_0 through Reagent_7 and ReagentCount_0 through ReagentCount_7.
    
    Args:
        csv_path: Path to the SpellReagents CSV file
        
    Returns:
        Dictionary mapping spell IDs to list of tuples (reagent_id, reagent_count)
    """
    reagents_mapping = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                spell_id = int(row['SpellID'])
                reagents_mapping[spell_id] = []
                
                # Process each reagent slot (0 through 7)
                for i in range(8):
                    reagent_id = int(row[f'Reagent_{i}'])
                    reagent_count = int(row[f'ReagentCount_{i}'])
                    
                    # Only add if both ID and count are positive
                    if reagent_id > 0 and reagent_count > 0:
                        reagents_mapping[spell_id].append((reagent_id, reagent_count))
                        
                # Remove spells with no reagents
                if not reagents_mapping[spell_id]:
                    del reagents_mapping[spell_id]
        
        logger.info(f"Loaded {len(reagents_mapping)} spells with reagents from CSV")
        return reagents_mapping
    
    except FileNotFoundError:
        logger.error(f"SpellReagents CSV file not found at: {csv_path}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing SpellReagents CSV file: {e}")
        raise

def load_modified_crafting_spell_slots(csv_path: str) -> Dict[int, List[Tuple[int, int]]]:
    """
    Load ModifiedCraftingSpellSlot.csv and map spell IDs to their modified reagent slots.
    
    Args:
        csv_path: Path to the ModifiedCraftingSpellSlot CSV file
        
    Returns:
        Dictionary mapping spell IDs to list of tuples (slot_id, reagent_count)
    """
    slot_mapping = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                spell_id = int(row['SpellID'])
                slot_id = int(row['ModifiedCraftingReagentSlotID'])
                reagent_count = int(row['ReagentCount'])
                
                if spell_id not in slot_mapping:
                    slot_mapping[spell_id] = []
                if reagent_count > 0:  # Only add if count is positive
                    slot_mapping[spell_id].append((slot_id, reagent_count))
        
        logger.info(f"Loaded {len(slot_mapping)} spells with modified crafting slots")
        return slot_mapping
    
    except FileNotFoundError:
        logger.error(f"ModifiedCraftingSpellSlot CSV file not found at: {csv_path}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing ModifiedCraftingSpellSlot CSV file: {e}")
        raise

def load_modified_reagent_slots(csv_path: str) -> Dict[int, str]:
    """
    Load ModifiedCraftingReagentSlot.csv and create mapping of slot IDs to reagent names.
    Only includes slots where ReagentType=1.
    
    Args:
        csv_path: Path to the ModifiedCraftingReagentSlot CSV file
        
    Returns:
        Dictionary mapping slot IDs to reagent names
    """
    slot_names = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                slot_id = int(row['ID'])
                reagent_type = int(row['ReagentType'])
                name = row['Name_lang'].strip()
                
                if reagent_type == 1 and name:  # Only include ReagentType=1 and non-empty names
                    # Fix specific reagent names
                    name = fix_reagent_name(name)
                    slot_names[slot_id] = name
        
        logger.info(f"Loaded {len(slot_names)} modified reagent slot names")
        return slot_names
    
    except FileNotFoundError:
        logger.error(f"ModifiedCraftingReagentSlot CSV file not found at: {csv_path}")
        raise
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing ModifiedCraftingReagentSlot CSV file: {e}")
        raise

def get_lowest_commodity_price_for_50(session: Session, item_ids: Set[int]) -> Optional[float]:
    """
    Get the lowest average price for 50 units from commodities for any of the given item IDs.
    
    Args:
        session: SQLAlchemy session
        item_ids: Set of item IDs to check
        
    Returns:
        Lowest average price for 50 units, or None if no prices found
    """
    if not item_ids:
        return None
    
    # Query all commodities for the given item IDs
    commodities = session.query(
        Commodity.item_id,
        Commodity.unit_price,
        Commodity.quantity
    ).filter(
        Commodity.item_id.in_(item_ids)
    ).order_by(
        Commodity.unit_price
    ).all()
    
    if not commodities:
        return None
    
    # Group by item_id and calculate average price for each
    item_prices = {}
    for item_id in item_ids:
        item_commodities = [c for c in commodities if c.item_id == item_id]
        if not item_commodities:
            continue
            
        total_quantity = 0
        total_price = 0
        remaining_units = 50
        
        for commodity in item_commodities:
            units_to_use = min(remaining_units, commodity.quantity)
            total_quantity += units_to_use
            total_price += units_to_use * commodity.unit_price
            remaining_units -= units_to_use
            
            if remaining_units <= 0:
                break
        
        if total_quantity == 50:  # Only consider if we found enough units
            avg_price = total_price / 50
            item_prices[item_id] = avg_price
            
    return min(item_prices.values()) if item_prices else None

def update_raw_craft_cost(
    session: Session,
    spell_reagents: Dict[int, List[Tuple[int, int]]],
    modified_slots: Dict[int, List[Tuple[int, int]]],
    slot_names: Dict[int, str],
    item_sparse: Dict[str, Set[int]]
) -> None:
    """
    Update raw_craft_cost for items based on their reagents' prices.
    
    Args:
        session: SQLAlchemy session
        spell_reagents: Mapping of spell IDs to reagent IDs and counts
        modified_slots: Mapping of spell IDs to modified slot IDs and counts
        slot_names: Mapping of slot IDs to reagent names
        item_sparse: Mapping of Display_lang to set of item IDs
    """
    try:
        # Get all items with spell_ids
        items = session.query(Item).filter(Item.spell_id.isnot(None)).all()
        updated_count = 0
        no_price_count = 0
        
        for item in items:
            total_cost = 0
            has_all_prices = True
            
            # Process direct reagents
            if item.spell_id in spell_reagents:
                for reagent_id, count in spell_reagents[item.spell_id]:
                    price = get_lowest_commodity_price_for_50(session, {reagent_id})
                    if price is None:
                        has_all_prices = False
                        logger.warning(f"No price found for reagent {reagent_id} of item {item.item_id}")
                        break
                    total_cost += price * count  # Adjust count relative to 50 units
            
            # Process modified crafting slots
            if has_all_prices and item.spell_id in modified_slots:
                for slot_id, count in modified_slots[item.spell_id]:
                    if slot_id not in slot_names:
                        continue
                        
                    # Find items matching the reagent name using ItemSparse data
                    reagent_name = slot_names[slot_id]
                    matching_ids = item_sparse.get(reagent_name, set())
                    
                    if not matching_ids:
                        logger.warning(f"No items found in ItemSparse for reagent name: {reagent_name}")
                        has_all_prices = False
                        break
                        
                    price = get_lowest_commodity_price_for_50(session, matching_ids)
                    if price is None:
                        has_all_prices = False
                        logger.warning(f"No price found for modified reagent {reagent_name}")
                        break
                    
                    total_cost += price * count  # Adjust count relative to 50 units
            
            if has_all_prices:
                item.raw_craft_cost = total_cost
                updated_count += 1
                logger.debug(f"Updated raw_craft_cost for item {item.item_id}: {total_cost}")
            else:
                no_price_count += 1
        
        session.commit()
        logger.info(f"Updated {updated_count} items with raw_craft_cost")
        logger.info(f"Could not update {no_price_count} items due to missing prices")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating items: {e}")
        raise

def main() -> None:
    """Main function to populate raw_craft_cost for items."""
    base_path = Path(__file__).parents[3] / "wow_db_file"
    
    spell_reagents_path = str(base_path / "SpellReagents.11.1.0.59095.csv")
    modified_slots_path = str(base_path / "ModifiedCraftingSpellSlot.11.1.0.59184.csv")
    reagent_slots_path = str(base_path / "ModifiedCraftingReagentSlot.11.1.0.59184.csv")
    item_sparse_path = str(base_path / "ItemSparse.11.1.0.59184.csv")
    
    try:
        # Load all required CSV data
        spell_reagents = load_spell_reagents(spell_reagents_path)
        modified_slots = load_modified_crafting_spell_slots(modified_slots_path)
        slot_names = load_modified_reagent_slots(reagent_slots_path)
        item_sparse = load_item_sparse(item_sparse_path)
        
        # Create database session
        engine = get_sync_engine()
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Update items with raw_craft_cost
            update_raw_craft_cost(session, spell_reagents, modified_slots, slot_names, item_sparse)
        finally:
            session.close()
            engine.dispose()
            
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()