# Item Name Enrichment System
# アイテム名の追加方法

## Overview / 概要

**Packets contain only item IDs, quantities, and prices.**
Item names are NOT included in the packet data and must be mapped manually from a master data file.

**パケットから抽出できるのは アイテムID、数量、価格 のみです。**
アイテム名はパケットに含まれていないため、手動でマスターデータに登録する必要があります。

✅ **Already Pre-populated:** The `data/item_master.json` file contains **6000+ items** with English names!

### 📋 Item Master Data Source

Item master data is sourced from the excellent [JordieB/bpsr_labs](https://github.com/JordieB/bpsr_labs) repository:
- **Source:** [item_name_map.json](https://github.com/JordieB/bpsr_labs/blob/main/data/game-data/item_name_map.json)
- **Items:** 6000+ game items with English names
- **Format:** Simple `"ID": "Name"` mapping
- **Credit:** Thanks to [@JordieB](https://github.com/JordieB) for maintaining this comprehensive database!

## 手順

### 1. パケットを解析（自動エンリッチメント）

```bat
tools\parse-pcap-v2.bat capture.pcap
```

これで：
- ✅ パケットをパース
- ✅ 自動的にアイテム名を付与
- ✅ 未知のアイテムをリスト表示
- ✅ `parsed_items_YYYYMMDD_HHMMSS.json` が生成されます（名前付き！）

**これだけで完了！** 別途エンリッチメントを実行する必要はありません。

### 2. マスターデータにアイテム名を追加（必要に応じて）

未知のアイテムが表示されたら、`data/item_master.json` を編集：

```json
{
  "85": "鉄鉱石",
  "100": "魔法の結晶",
  "1401": "伝説の剣"
}
```

### 3. 再度パース実行

```bat
tools\parse-pcap-v2.bat capture.pcap
```

今度は正しいアイテム名が付与されます！

## アイテム名の調べ方

### 方法1: ゲーム内で確認
1. ゲーム内の取引所でアイテムを確認
2. アイテムIDと名前をメモ
3. `data/item_master.json` に追加

### 方法2: ゲームのデータベースファイルから抽出
- ゲームのインストールフォルダから `items.db` や `master.db` などを探す
- SQLiteビューアで開く
- アイテムテーブルをエクスポート

### 方法3: コミュニティWikiから
- 攻略Wikiやデータベースサイトからアイテム情報を取得
- IDと名前の対応表を作成

## 出力例

### エンリッチメント前
```json
{
  "listing_id": 2207121,
  "item_id": 85,
  "item_name": "",
  "quantity": 1,
  "price": 2207121,
  "unit_price": 2207121
}
```

### エンリッチメント後
```json
{
  "listing_id": 2207121,
  "item_id": 85,
  "item_name": "鉄鉱石",
  "category": "素材",
  "quantity": 1,
  "price": 2207121,
  "unit_price": 2207121
}
```

## データベースへのインポート

アイテム名が付与されたら、データベースにインポートできます：

```bat
python scripts\import_from_json.py parsed_items_20260128_123456_enriched.json
```

## ヒント

- 少しずつアイテム名を追加していく
- よく取引されるアイテムから優先的に追加
- コミュニティで共有すれば全員が楽に！
