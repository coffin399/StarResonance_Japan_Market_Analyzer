"""
Sample data import script
サンプルデータをインポートするスクリプト
"""
import sys
sys.path.insert(0, '.')

from datetime import datetime, timedelta
import random
from src.database import SessionLocal, Item, Listing, PriceHistory


def create_sample_items(db):
    """サンプルアイテムを作成"""
    items = [
        {"id": 1, "name": "高級素材", "category": "材料", "rarity": "SR"},
        {"id": 2, "name": "レアな鉱石", "category": "材料", "rarity": "R"},
        {"id": 3, "name": "強化石", "category": "強化", "rarity": "SR"},
        {"id": 4, "name": "回復薬（大）", "category": "消耗品", "rarity": "N"},
        {"id": 5, "name": "経験値ブースト", "category": "消耗品", "rarity": "R"},
        {"id": 6, "name": "レアな装備", "category": "装備", "rarity": "SSR"},
        {"id": 7, "name": "料理素材", "category": "材料", "rarity": "N"},
        {"id": 8, "name": "魔法の結晶", "category": "材料", "rarity": "SR"},
        {"id": 9, "name": "装飾品の欠片", "category": "材料", "rarity": "R"},
        {"id": 10, "name": "バフアイテム", "category": "消耗品", "rarity": "R"},
    ]
    
    for item_data in items:
        item = Item(**item_data)
        db.add(item)
    
    db.commit()
    print(f"✓ {len(items)}個のアイテムを作成しました")


def create_sample_listings(db):
    """サンプル出品を作成"""
    items = db.query(Item).all()
    base_prices = {
        1: 10000,
        2: 5000,
        3: 15000,
        4: 500,
        5: 3000,
        6: 100000,
        7: 200,
        8: 20000,
        9: 8000,
        10: 2000,
    }
    
    listing_id = 1000000
    
    for item in items:
        base_price = base_prices.get(item.id, 1000)
        
        # 各アイテムに5-15件の出品を作成
        num_listings = random.randint(5, 15)
        
        for i in range(num_listings):
            # 価格にランダムな変動を加える
            price_variation = random.uniform(0.8, 1.3)
            quantity = random.randint(1, 50)
            price = int(base_price * price_variation * quantity)
            
            listing = Listing(
                id=listing_id,
                item_id=item.id,
                quantity=quantity,
                price=price,
                unit_price=price // quantity,
                seller_name=f"プレイヤー{random.randint(1, 100)}",
                status="active",
                captured_at=datetime.utcnow() - timedelta(hours=random.randint(0, 48))
            )
            db.add(listing)
            listing_id += 1
    
    db.commit()
    print(f"✓ {listing_id - 1000000}件の出品を作成しました")


def create_sample_price_history(db):
    """サンプル価格履歴を作成"""
    items = db.query(Item).all()
    base_prices = {
        1: 10000,
        2: 5000,
        3: 15000,
        4: 500,
        5: 3000,
        6: 100000,
        7: 200,
        8: 20000,
        9: 8000,
        10: 2000,
    }
    
    # 過去30日分の価格履歴を作成
    for item in items:
        base_price = base_prices.get(item.id, 1000)
        current_price = base_price
        
        for days_ago in range(30, 0, -1):
            # トレンドをシミュレート
            trend = random.choice([-0.05, -0.02, 0, 0, 0.02, 0.05])
            current_price = int(current_price * (1 + trend))
            
            # ランダムな変動
            min_price = int(current_price * 0.9)
            max_price = int(current_price * 1.1)
            avg_price = (min_price + max_price) / 2
            
            history = PriceHistory(
                item_id=item.id,
                price=current_price,
                quantity=random.randint(10, 100),
                unit_price=current_price // random.randint(1, 10),
                min_price=min_price,
                max_price=max_price,
                avg_price=avg_price,
                total_listings=random.randint(5, 20),
                recorded_at=datetime.utcnow() - timedelta(days=days_ago)
            )
            db.add(history)
    
    db.commit()
    print("✓ 価格履歴を作成しました")


def main():
    """メイン処理"""
    print("サンプルデータをインポートしています...\n")
    
    db = SessionLocal()
    
    try:
        # 既存のデータをクリア（オプション）
        print("既存のデータをクリアしています...")
        db.query(PriceHistory).delete()
        db.query(Listing).delete()
        db.query(Item).delete()
        db.commit()
        print("✓ クリア完了\n")
        
        # サンプルデータを作成
        create_sample_items(db)
        create_sample_listings(db)
        create_sample_price_history(db)
        
        print("\n✅ サンプルデータのインポートが完了しました！")
        print("\nAPIサーバーを起動して以下のURLにアクセスしてください:")
        print("  http://localhost:8000")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ エラーが発生しました: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
