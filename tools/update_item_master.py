"""
Item Master Data Updater
Converts item ID/name JSON to item_master.json format
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# User provided item data (partial - add more as needed)
USER_ITEM_DATA = {
    "1": "Judgment Blade- Scythe Long Blade",
    "2": "Frostjade Staff - Magic Wand",
    "3": "Scourgefire Axe - Battle Axe",
    "4": "Justice Lance- Lance",
    "5": "Fatewood Ring - Magic Ring",
    "8": "Thunder Flash - Hand Cannon",
    "9": "Sandward - Blade",
    "10": "(Temporary) Rorola",
    "11": "Bow",
    "12": "Frostjade Staff - Magic Wand",
    "22": "Unknown Item #22",  # Add actual name when discovered
    "26": "Unknown Item #26",
    "29": "Unknown Item #29",
    "59": "Unknown Item #59",
    "79": "Unknown Item #79",
    "85": "Unknown Item #85",
    "86": "Unknown Item #86",
    "88": "Unknown Item #88",
    "94": "Unknown Item #94",
    "100": "Unknown Item #100",
    "106": "Unknown Item #106",
    "109": "Unknown Item #109",
    "121": "Unknown Item #121",
    "132": "Unknown Item #132",
    "257": "Unknown Item #257",
    "1401": "Unknown Item #1401",
    "201": "EXP",
    "202": "EXP (blessing)",
    "301": "Season Pass EXP",
    "302": "Season Pass EXP (Not counted toward weekly limit)",
    "10001": "Season 1 Points",
    "10002": "Luno",
    "10003": "Rose Orb",
    "10004": "Friendship Points",
    "10005": "Rose Orb (Bound)",
    "10006": "Honor Coin",
    "10007": "Supply Points",
    "10008": "Luno (Bound)",
    "10009": "Meow Coin",
    "10010": "Homestead Coins",
    "10011": "Reclaim Token",
    "10013": "Rose Orb",
    "11001": "Silver Star Badge",
    "11002": "Adept's Badge",
    "20001": "Energy Points",
    "20002": "Monster Hunt EXP",
    "20003": "Focus",
    "20006": "Emblem Power Parts",
    "20010": "World Boss Crusade Points",
    "20011": "Meowlux Points",
    "30001": "Talent Points",
    # Add more items here as they are discovered in-game
}

def categorize_item(item_id: str, name: str) -> str:
    """Categorize item based on ID range and name"""
    try:
        id_int = int(item_id)
        
        # Currency items
        if id_int >= 10000 and id_int < 40000:
            return "currency"
        
        # Consumables
        if id_int >= 1010000 and id_int < 1016000:
            return "consumable"
        
        # Equipment
        if id_int >= 1040000:
            return "equipment"
        
        # Materials
        if id_int >= 1052000:
            return "material"
        
        # Weapons (low IDs)
        if id_int < 20:
            return "weapon"
        
        # Skills/EXP
        if "EXP" in name or "Mastery" in name:
            return "skill"
        
        # Default
        return "misc"
        
    except ValueError:
        return "misc"

def update_item_master():
    """Update item_master.json with user provided data"""
    master_file = project_root / "data" / "item_master.json"
    
    # Load existing data
    if master_file.exists():
        with open(master_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"items": {}, "_comment": "Item master data for Blue Protocol: Star Resonance"}
    
    # Update with new items
    for item_id, item_name in USER_ITEM_DATA.items():
        category = categorize_item(item_id, item_name)
        data["items"][item_id] = {
            "name": item_name,
            "category": category
        }
    
    # Save back
    with open(master_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated {len(USER_ITEM_DATA)} items in {master_file}")
    print(f"Total items in database: {len(data['items'])}")

if __name__ == "__main__":
    update_item_master()
