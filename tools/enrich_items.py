"""
Enrich parsed items with names from master data
パースしたアイテムにマスターデータから名前を付与
"""
import sys
import json
from pathlib import Path

def load_item_master(master_file: str = 'data/item_master.json') -> dict:
    """アイテムマスターデータを読み込み"""
    master_path = Path(master_file)
    
    if not master_path.exists():
        print(f"Warning: Item master not found: {master_file}")
        print("Creating empty master file...")
        master_path.parent.mkdir(parents=True, exist_ok=True)
        with open(master_path, 'w', encoding='utf-8') as f:
            json.dump({"items": {}, "_comment": "Add item names here"}, f, ensure_ascii=False, indent=2)
        return {}
    
    with open(master_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
        # 新形式: {"items": {...}} の場合
        if isinstance(data, dict) and 'items' in data:
            return data['items']
        
        # シンプル形式: {"ID": "名前", ...} の場合
        # 文字列値をname付きの辞書に変換
        if isinstance(data, dict):
            normalized = {}
            for key, value in data.items():
                if key.startswith('_'):  # コメントフィールドをスキップ
                    continue
                if isinstance(value, str):
                    # シンプル形式: "ID": "名前"
                    normalized[key] = {"name": value, "category": "misc"}
                elif isinstance(value, dict):
                    # 既に辞書形式
                    normalized[key] = value
            return normalized
        
        return {}

def enrich_items(input_file: str, output_file: str = None, master_file: str = 'data/item_master.json'):
    """アイテムデータに名前を付与"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}")
        return
    
    # 入力ファイル読み込み
    with open(input_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    # マスターデータ読み込み
    item_master = load_item_master(master_file)
    
    # アイテム名を付与
    enriched = 0
    for item in items:
        item_id_str = str(item['item_id'])
        
        if item_id_str in item_master:
            master_data = item_master[item_id_str]
            
            # master_dataが辞書の場合
            if isinstance(master_data, dict):
                item_name = master_data.get('name', f'Item #{item_id_str}')
                category = master_data.get('category', 'misc')
            # master_dataが文字列の場合（シンプル形式）
            else:
                item_name = master_data
                category = 'misc'
            
            # 新形式 (analysis フィールドあり)
            if 'analysis' in item:
                item['analysis']['item_name'] = item_name
                item['analysis']['category'] = category
            # 旧形式 (直接フィールド)
            else:
                item['item_name'] = item_name
                item['category'] = category
            
            enriched += 1
        else:
            # 新形式
            if 'analysis' in item:
                if not item['analysis'].get('item_name'):
                    item['analysis']['item_name'] = f'Unknown Item #{item_id_str}'
            # 旧形式
            else:
                if not item.get('item_name'):
                    item['item_name'] = f'Unknown Item #{item_id_str}'
    
    # 出力ファイル名決定
    if output_file is None:
        output_file = input_path.stem + '_enriched' + input_path.suffix
    
    output_path = Path(output_file)
    
    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Enrichment Complete")
    print(f"{'='*80}")
    print(f"Input:  {input_file}")
    print(f"Output: {output_path}")
    print(f"Total items: {len(items)}")
    print(f"Enriched: {enriched}")
    print(f"Unknown: {len(items) - enriched}")
    
    # 未知のアイテムIDをリスト表示
    unknown_ids = set()
    for item in items:
        item_id_str = str(item['item_id'])
        if item_id_str not in item_master:
            unknown_ids.add(item_id_str)
    
    if unknown_ids:
        print(f"\nUnknown Item IDs (add these to {master_file}):")
        for item_id in sorted(unknown_ids, key=int):
            print(f'  "{item_id}": {{"name": "アイテム名を入力", "category": "カテゴリ"}},')
    
    return str(output_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python enrich_items.py <parsed_items.json> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    enrich_items(input_file, output_file)

if __name__ == '__main__':
    main()
