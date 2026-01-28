# Quick Start: Item Names
# クイックスタート: アイテム名

## TL;DR

```bat
# 1. Parse packets (auto-enrichment included!)
tools\parse-pcap-v2.bat capture.pcap

# 2. Done! Check the parsed_items_*.json file (names already added!)
```

---

## Why Item Names Are Not In Packets
## なぜアイテム名がパケットにないのか

**Game packets only contain:**
- Item ID (数値のアイテムID)
- Quantity (数量)
- Price (価格)

**Item names are stored in the game client, not transmitted over the network.**

This is normal for most online games - they send minimal data and let the client look up the display names locally.

---

## Solution: Item Master Database
## 解決策: アイテムマスターデータベース

We maintain `data/item_master.json` - a mapping of item IDs to names:

```json
{
  "items": {
    "10002": {
      "name": "Luno",
      "category": "currency"
    },
    "85": {
      "name": "Unknown Item #85",
      "category": "misc"
    }
  }
}
```

✅ **Already includes 116+ common items!**

---

## How To Use
## 使い方

### Step 1: Parse Your Packet Capture

```bat
tools\parse-pcap-v2.bat your_capture.pcap
```

Output: `parsed_items_YYYYMMDD_HHMMSS.json`

### Step 2: Results Are Auto-Enriched!

**The parser automatically enriches items!**

Output already includes item names from `data/item_master.json`:

```json
{
  "item_id": 10002,
  "item_name": "Luno",
  "category": "currency",
  "price": 5000,
  "quantity": 100
}
```

**Console shows unknown items:**

```
================================================================================
Unknown items found: 7
================================================================================
Add these to data/item_master.json:
  "85": "Item Name Here",
  "121": "Item Name Here",
```

### Step 3: Add Unknown Items (Optional)

Open `data/item_master.json` and add discovered items:

```json
{
  "85": "Iron Ore",
  "121": "Magic Crystal"
}
```

Then re-parse:
```bat
tools\parse-pcap-v2.bat capture.pcap
```

Now those items will have proper names!

---

## Finding Item Names
## アイテム名の調べ方

### Method 1: In-Game (一番確実)

1. Open Trading Center
2. Note the item ID from the URL or hover tooltip
3. Note the item name displayed
4. Add to `data/item_master.json`

### Method 2: Game Database Files

Some games store item data in SQLite files:
- Look in game install directory for `*.db` files
- Open with DB Browser for SQLite
- Export item tables

### Method 3: Community Wiki

- Check game wikis/databases
- Look for item ID lists
- Many communities share item databases

### Method 4: Share with Community

- Share your `item_master.json` additions with other users
- Build a community database together!

---

## Pre-Populated Items
## すでに登録済みのアイテム

The tool comes with **6000+ items** pre-populated from [JordieB/bpsr_labs](https://github.com/JordieB/bpsr_labs)!

**Source:** [item_name_map.json](https://github.com/JordieB/bpsr_labs/blob/main/data/game-data/item_name_map.json)

**Examples:**

**Currencies:**
- 10002: Luno
- 10003: Rose Orb
- 10004: Friendship Points
- 10006: Honor Coin
- 10009: Meow Coin
- And more...

**Weapons:**
- 1: Judgment Blade
- 2: Frostjade Staff
- 3: Scourgefire Axe
- And more...

**Consumables:**
- 1010001: Recovery Potion
- 1010011: Canned Fish Lv.1
- 1010021: Grilled Fish Lv.1
- And more...

Check `data/item_master.json` for the full list!

---

## Categories
## カテゴリ

- `weapon` - Weapons / 武器
- `armor` - Armor, Equipment / 防具・装備
- `consumable` - Potions, Food / ポーション・料理
- `material` - Crafting Materials / 素材
- `currency` - Luno, Rose Orbs / 通貨
- `skill` - EXP, Mastery / 経験値・熟練度
- `misc` - Other / その他

Categories help with:
- Filtering in web UI
- Market analysis
- Profit calculations

---

## Advanced: Batch Update Items
## 上級: 一括でアイテムを追加

Edit `tools/update_item_master.py` and add items to `USER_ITEM_DATA`:

```python
USER_ITEM_DATA = {
    "85": "Iron Ore",
    "100": "Magic Essence",
    "121": "Fire Crystal",
    # Add more...
}
```

Then run:
```bat
py -3.10 tools/update_item_master.py
```

This updates `data/item_master.json` automatically!

---

## Need More Help?
## さらなるヘルプが必要？

- Full workflow: [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)
- Item system details: [README_ITEM_NAMES.md](README_ITEM_NAMES.md)
- Installation help: [INSTALL_GUIDE.md](INSTALL_GUIDE.md)

---

## Summary
## まとめ

1. ✅ Parse packets → Get item IDs, quantities, prices
2. ✅ Enrich with item_master.json → Get item names
3. ✅ Gradually add unknown items as you discover them
4. ✅ Share your item_master.json with the community!

**パケットにはアイテム名が含まれていません。**
**でも、アイテムマスターデータで簡単に名前を追加できます！**

Happy trading! / 良い取引を！
