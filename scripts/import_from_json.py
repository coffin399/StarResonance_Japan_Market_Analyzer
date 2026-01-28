"""
Import parsed items from JSON to database
パース済みのJSONファイルからデータベースにインポート
"""
import sys
sys.path.insert(0, '.')

import json
import logging
from pathlib import Path
from datetime import datetime

from src.database import SessionLocal, Item, Listing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_from_json(json_file: str):
    """
    JSONファイルからデータベースにインポート
    
    Args:
        json_file: JSONファイルのパス
    """
    logger.info(f"Importing from: {json_file}")
    
    # JSONファイルを読み込み
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    items_data = data.get('items', [])
    logger.info(f"Found {len(items_data)} items in JSON")
    
    if not items_data:
        logger.warning("No items to import")
        return 0
    
    # データベースセッション
    db = SessionLocal()
    
    try:
        imported_count = 0
        skipped_count = 0
        
        for item_data in items_data:
            item_id = item_data.get('item_id')
            item_name = item_data.get('item_name', 'Unknown')
            
            if not item_id:
                logger.debug(f"Skipping item without ID: {item_name}")
                skipped_count += 1
                continue
            
            # アイテムを取得または作成
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                item = Item(
                    id=item_id,
                    name=item_name
                )
                db.add(item)
                logger.info(f"Created new item: {item_name} (ID: {item_id})")
            
            # リスティングを作成
            listing_id = item_data.get('listing_id', 0)
            if listing_id == 0:
                # IDがない場合はタイムスタンプベースで生成
                listing_id = int(datetime.now().timestamp() * 1000000) + imported_count
            
            # 既存のリスティングをチェック
            existing = db.query(Listing).filter(Listing.id == listing_id).first()
            if existing:
                logger.debug(f"Listing {listing_id} already exists, skipping")
                skipped_count += 1
                continue
            
            listing = Listing(
                id=listing_id,
                item_id=item_id,
                quantity=item_data.get('quantity', 1),
                price=item_data.get('price', 0),
                unit_price=item_data.get('unit_price', 0),
                seller_name="パース済み",
                status="active",
                captured_at=datetime.now()
            )
            db.add(listing)
            imported_count += 1
        
        # コミット
        db.commit()
        logger.info(f"Import complete: {imported_count} items imported, {skipped_count} skipped")
        
        return imported_count
    
    except Exception as e:
        db.rollback()
        logger.error(f"Import failed: {e}")
        raise
    
    finally:
        db.close()


def main():
    """メイン処理"""
    print("=" * 60)
    print("Import Parsed Items to Database")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python import_from_json.py <json_file>")
        print()
        print("Example:")
        print("  python scripts\\import_from_json.py parsed_items_20260128_123456.json")
        print()
        return 1
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"Error: File not found: {json_file}")
        return 1
    
    try:
        count = import_from_json(json_file)
        print()
        print("=" * 60)
        print(f"Successfully imported {count} items!")
        print("=" * 60)
        print()
        print("You can now view the data at http://localhost:8000")
        print()
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
