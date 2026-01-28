# Item Name Enrichment System
# アイテム名の追加方法

## Overview / 概要

**Packets contain only item IDs, quantities, and prices.**
Item names are NOT included in the packet data and must be mapped manually from a master data file.

**パケットから抽出できるのは アイテムID、数量、価格 のみです。**
アイテム名はパケットに含まれていないため、手動でマスターデータに登録する必要があります。

✅ **Already Pre-populated:** The `data/item_master.json` file contains 116+ common items based on game data.

## 手順

### 1. パケットを解析

```bat
tools\parse-pcap-v2.bat capture.pcap
```

これで `parsed_items_YYYYMMDD_HHMMSS.json` が生成されます。

### 2. アイテム名を付与

```bat
tools\enrich-items.bat parsed_items_20260128_123456.json
```

これで以下が生成されます：
- `parsed_items_20260128_123456_enriched.json` - 名前付きデータ
- 未知のアイテムIDのリスト（コンソールに表示）

### 3. マスターデータにアイテム名を追加

`data/item_master.json` を編集：

```json
{
  "items": {
    "85": {
      "name": "鉄鉱石",
      "category": "素材"
    },
    "100": {
      "name": "魔法の結晶",
      "category": "素材"
    },
    "1401": {
      "name": "伝説の剣",
      "category": "武器"
    }
  }
}
```

### 4. 再度エンリッチメント実行

```bat
tools\enrich-items.bat parsed_items_20260128_123456.json
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
