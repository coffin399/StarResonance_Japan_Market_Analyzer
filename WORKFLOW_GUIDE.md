# Complete Workflow Guide
# 完全なワークフローガイド

## Quick Start / クイックスタート

### 1. Capture Game Packets / ゲームパケットをキャプチャ

**Using Wireshark (推奨):**
1. Open Wireshark
2. Start capturing on your network interface
3. Apply filter: `tcp.port == [game_port]` (replace with actual game port)
4. Browse the Trading Center in-game
5. Stop capture and save as `capture.pcap`

### 2. Parse Packet Data / パケットデータを解析

```bat
tools\parse-pcap-v2.bat capture.pcap
```

**Output:**
- `parsed_items_YYYYMMDD_HHMMSS.json` - Extracted item data with names already included!
- Console shows enrichment statistics and unknown item IDs

**Auto-enrichment included!** No separate step needed.

### 4. Import to Database / データベースにインポート

```bat
python scripts\import_from_json.py parsed_items_YYYYMMDD_HHMMSS_enriched.json
```

### 5. View in Web Interface / Web画面で確認

```bat
start.bat
```

Then open: http://localhost:8000

---

## Detailed Workflow / 詳細なワークフロー

## Step 1: Environment Setup / 環境セットアップ

### First Time Installation

```bat
quick-install.bat
```

This will:
- Create virtual environment
- Install all dependencies
- Setup database

## Step 2: Packet Capture / パケットキャプチャ

### Option A: Wireshark (Manual)

1. **Install Wireshark + Npcap**
   - Download: https://www.wireshark.org/download.html
   - Install with Npcap support

2. **Configure Filter**
   ```
   tcp.port == [game_port] && tcp.len > 0
   ```

3. **Capture**
   - Start capture
   - Navigate to Trading Center in-game
   - Browse items, check prices
   - Stop capture after 1-2 minutes

4. **Save**
   - File → Save As → `capture.pcap`

### Option B: Real-time Capture (Experimental)

```bat
tools\analyze-traffic.bat
```

Select option 2 for real-time capture.

## Step 3: Packet Parsing / パケット解析

### Parse Captured Data

```bat
tools\parse-pcap-v2.bat capture.pcap
```

**What it does:**
- Searches for game packets (magic bytes: `00 63 33 53 42 00`)
- Extracts Protobuf data
- Identifies item IDs, quantities, prices
- Outputs to JSON file

**Output Format:**
```json
[
  {
    "listing_id": 2207121,
    "item_id": 85,
    "item_name": "",
    "quantity": 1,
    "price": 2207121,
    "unit_price": 2207121
  }
]
```

## Step 4: Item Name Enrichment / アイテム名の付与

### Enrich Parsed Data

```bat
tools\enrich-items.bat parsed_items_20260128_123456.json
```

**What it does:**
- Loads `data/item_master.json`
- Maps item IDs to names
- Adds category information
- Creates enriched output file

**Output Format:**
```json
[
  {
    "listing_id": 2207121,
    "item_id": 10002,
    "item_name": "Luno",
    "category": "currency",
    "quantity": 100,
    "price": 5000,
    "unit_price": 50
  }
]
```

### Adding Unknown Items

If enrichment shows unknown item IDs:

1. Open `data/item_master.json`
2. Add the item:
```json
{
  "items": {
    "85": {
      "name": "Iron Ore",
      "category": "material"
    }
  }
}
```

3. Run enrichment again:
```bat
tools\enrich-items.bat parsed_items_20260128_123456.json
```

**Categories:**
- `weapon` - Weapons
- `armor` - Armor/Equipment
- `consumable` - Potions, Food
- `material` - Crafting materials
- `currency` - Luno, Rose Orbs, etc.
- `misc` - Other items

## Step 5: Database Import / データベースへのインポート

```bat
python scripts\import_from_json.py parsed_items_20260128_123456.json
```

**What it does:**
- Connects to SQLite database
- Creates `Item` and `Listing` records
- Updates price history
- Calculates trends

## Step 6: View and Analyze / 確認と分析

### Start Web Server

```bat
start.bat
```

### Access Dashboard

Open browser: http://localhost:8000

**Features:**
- View all items with current prices
- Price history charts
- Profit calculations
- Market trends

### API Access

```bash
# Get all items
curl http://localhost:8000/api/items

# Get specific item
curl http://localhost:8000/api/items/10002

# Get price history
curl http://localhost:8000/api/items/10002/history
```

---

## Advanced Usage / 高度な使い方

### Real-time Price Monitoring

```bash
# Start API server
start.bat

# In another terminal, start real-time capture
python examples/realtime_capture_example.py
```

### Discord Bot Integration

Use the API endpoints in your Discord bot:

```python
import requests

def get_item_price(item_id):
    response = requests.get(f'http://localhost:8000/api/items/{item_id}')
    return response.json()

# Example: Get Luno price
luno_data = get_item_price(10002)
print(f"Luno price: {luno_data['current_price']}")
```

### Profit Calculator

```python
import requests

def calculate_profit(item_id, buy_price, sell_price, quantity):
    # Trading Center tax is typically 5%
    tax_rate = 0.05
    
    gross_profit = (sell_price - buy_price) * quantity
    tax = sell_price * quantity * tax_rate
    net_profit = gross_profit - tax
    
    return {
        'gross_profit': gross_profit,
        'tax': tax,
        'net_profit': net_profit,
        'roi': (net_profit / (buy_price * quantity)) * 100
    }
```

---

## Troubleshooting / トラブルシューティング

### Packet Capture Issues

**Problem:** No packets captured
- **Solution:** Make sure you're capturing the correct network interface
- Check if the game uses a different port
- Try capturing without filters first

**Problem:** Wrong packets captured
- **Solution:** Verify magic bytes: `00 63 33 53 42 00`
- Use `tools\analyze-traffic.bat` option 4 to search for magic bytes

### Parsing Issues

**Problem:** No items extracted
- **Solution:** The packet structure might have changed
- Check `tools/README.md` for parser updates
- Report the issue with sample `.pcap` file (anonymized)

**Problem:** Wrong prices/quantities
- **Solution:** The Protobuf structure may have changed
- Try the original parser: `tools\parse-pcap.bat`

### Item Name Issues

**Problem:** All items show as "Unknown Item #XX"
- **Solution:** The `data/item_master.json` needs to be populated
- Follow the enrichment guide in `README_ITEM_NAMES.md`
- Gradually add item names as you discover them in-game

### Database Issues

**Problem:** Import fails
- **Solution:** Run `start.bat` first to initialize the database
- Check if `data/market.db` exists
- Try deleting the database and re-running `start.bat`

---

## File Structure / ファイル構造

```
StarResonance_Japan_Market_Analyzer/
├── data/
│   ├── item_master.json          # Item ID → Name mapping
│   └── market.db                  # SQLite database
├── tools/
│   ├── parse-pcap-v2.bat          # Parse .pcap files
│   ├── enrich-items.bat           # Add item names
│   ├── analyze-traffic.bat        # Interactive analyzer
│   ├── packet_parser_v2.py        # Protobuf parser
│   └── enrich_items.py            # Enrichment script
├── scripts/
│   └── import_from_json.py        # JSON → Database importer
├── src/
│   ├── api/                       # FastAPI backend
│   ├── database/                  # Database models
│   └── packet_decoder/            # Packet decoders
├── web/
│   └── static/                    # Web frontend
├── quick-install.bat              # Quick setup
├── start.bat                      # Start web server
└── README.md                      # Main documentation
```

---

## Tips and Best Practices / ヒントとベストプラクティス

### Efficient Packet Capture

1. **Capture during peak hours** - More listings = more data
2. **Browse multiple pages** - Get comprehensive price data
3. **Capture regularly** - Track price trends over time

### Item Master Maintenance

1. **Prioritize high-value items** - Add names for expensive/popular items first
2. **Community collaboration** - Share your `item_master.json` with others
3. **Backup regularly** - Keep a copy of your item master data

### Market Analysis

1. **Look for arbitrage opportunities** - Buy low, sell high
2. **Track price trends** - Identify market patterns
3. **Monitor supply/demand** - Adjust strategies accordingly

### External Access (Cloudflare Tunnel)

For Discord bot or external access:

1. Install Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/
2. Run tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:8000
   ```
3. Use the provided URL in your Discord bot

---

## Contributing / 貢献

If you discover new item IDs/names or improve the parsers:

1. Update `data/item_master.json` with new items
2. Test with `tools\enrich-items.bat`
3. Share your updated `item_master.json` with the community!

---

## Support / サポート

- Check `README.md` for general information
- Read `tools/README.md` for parser details
- See `README_ITEM_NAMES.md` for item enrichment
- Review `INSTALL_GUIDE.md` for installation help

Happy trading! 良い取引を！
