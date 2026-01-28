# API リファレンス

Star Resonance Market Analyzer の REST API ドキュメントです。

## ベースURL

```
http://localhost:8000/api/v1
```

本番環境:
```
https://your-domain.com/api/v1
```

## 認証

現在、APIは認証なしで利用可能です。本番環境では適切な認証を実装することを推奨します。

---

## アイテム (Items)

### GET /items

アイテム一覧を取得します。

**クエリパラメータ:**
- `skip` (int, optional): スキップする件数（デフォルト: 0）
- `limit` (int, optional): 取得する件数（デフォルト: 100、最大: 1000）
- `category` (string, optional): カテゴリでフィルタ
- `search` (string, optional): アイテム名で検索

**レスポンス例:**
```json
[
  {
    "id": 1,
    "name": "高級素材",
    "name_en": "Premium Material",
    "category": "材料",
    "rarity": "SR",
    "icon_url": "https://example.com/icon1.png"
  }
]
```

### GET /items/{item_id}

特定のアイテムの詳細情報を取得します。

**パラメータ:**
- `item_id` (int): アイテムID

**レスポンス例:**
```json
{
  "id": 1,
  "name": "高級素材",
  "category": "材料",
  "rarity": "SR",
  "latest_listings": [...],
  "min_price": 1000,
  "max_price": 1500,
  "avg_price": 1250,
  "total_listings": 10
}
```

### GET /items/{item_id}/history

アイテムの価格履歴を取得します。

**パラメータ:**
- `item_id` (int): アイテムID
- `days` (int, optional): 取得する日数（デフォルト: 7、最大: 90）

**レスポンス例:**
```json
[
  {
    "id": 1,
    "item_id": 1,
    "price": 1200,
    "quantity": 10,
    "unit_price": 120,
    "min_price": 1000,
    "max_price": 1500,
    "avg_price": 1250.5,
    "total_listings": 15,
    "recorded_at": "2026-01-28T12:00:00"
  }
]
```

### GET /items/{item_id}/lowest-price

アイテムの最安値を取得します。

**レスポンス例:**
```json
{
  "item_id": 1,
  "lowest_price": 1000,
  "quantity": 10,
  "unit_price": 100,
  "seller": "プレイヤー名",
  "captured_at": "2026-01-28T12:00:00"
}
```

---

## 出品情報 (Listings)

### GET /listings

出品情報一覧を取得します。

**クエリパラメータ:**
- `skip` (int, optional): スキップする件数
- `limit` (int, optional): 取得する件数
- `item_id` (int, optional): アイテムIDでフィルタ
- `status` (string, optional): ステータス（active, sold, expired）
- `sort_by` (string, optional): ソートフィールド（price, captured_at）
- `order` (string, optional): ソート順（asc, desc）

**レスポンス例:**
```json
[
  {
    "id": 123456789,
    "item_id": 1,
    "quantity": 10,
    "price": 10000,
    "unit_price": 1000,
    "seller_name": "プレイヤー名",
    "status": "active",
    "captured_at": "2026-01-28T12:00:00"
  }
]
```

### GET /listings/{listing_id}

特定の出品情報を取得します。

**レスポンス例:**
```json
{
  "id": 123456789,
  "item_id": 1,
  "item_name": "高級素材",
  "quantity": 10,
  "price": 10000,
  "unit_price": 1000,
  "seller_name": "プレイヤー名",
  "status": "active",
  "captured_at": "2026-01-28T12:00:00",
  "expires_at": "2026-02-04T12:00:00"
}
```

### GET /listings/latest/all

最新の出品情報を取得します。

**クエリパラメータ:**
- `limit` (int, optional): 取得する件数（デフォルト: 50、最大: 500）

### GET /listings/trending

トレンドアイテムを取得します。

**クエリパラメータ:**
- `hours` (int, optional): 集計期間（時間）（デフォルト: 24、最大: 168）
- `limit` (int, optional): 取得する件数

**レスポンス例:**
```json
[
  {
    "item_id": 1,
    "item_name": "高級素材",
    "listing_count": 50,
    "min_price": 1000,
    "max_price": 1500,
    "avg_price": 1250.5
  }
]
```

---

## 統計 (Statistics)

### GET /statistics/market-overview

市場全体の概要を取得します。

**レスポンス例:**
```json
{
  "active_listings": 1500,
  "unique_items": 250,
  "total_value": 50000000,
  "new_listings_24h": 120,
  "updated_at": "2026-01-28T12:00:00"
}
```

### GET /statistics/daily

日次統計を取得します。

**クエリパラメータ:**
- `days` (int, optional): 取得する日数（デフォルト: 30、最大: 365）

### GET /statistics/price-distribution

特定アイテムの価格分布を取得します。

**クエリパラメータ:**
- `item_id` (int, required): アイテムID

**レスポンス例:**
```json
{
  "item_id": 1,
  "distribution": [
    {"range": "1000-1100", "count": 5},
    {"range": "1100-1200", "count": 10}
  ],
  "total": 50,
  "min_price": 1000,
  "max_price": 1500,
  "avg_price": 1250.5
}
```

### GET /statistics/top-sellers

トップセラーを取得します。

**クエリパラメータ:**
- `limit` (int, optional): 取得する件数
- `days` (int, optional): 集計期間（日数）

### GET /statistics/category-breakdown

カテゴリ別の出品状況を取得します。

---

## 損益計算 (Profit Calculator)

### POST /calculate-profit

取引の損益を計算します。

**リクエストボディ:**
```json
{
  "item_id": 1,
  "buy_price": 1000,
  "sell_price": 1500,
  "quantity": 10,
  "fee_rate": 0.05,
  "has_monthly_card": false
}
```

**レスポンス例:**
```json
{
  "item_id": 1,
  "item_name": "高級素材",
  "quantity": 10,
  "buy_price": 1000,
  "sell_price": 1500,
  "total_buy_cost": 10000,
  "total_sell_revenue": 15000,
  "fee": 750,
  "fee_rate": 0.05,
  "net_revenue": 14250,
  "profit": 4250,
  "profit_rate": 42.5,
  "roi": 0.425
}
```

### POST /calculate-optimal-price

目標利益率を達成するための最適販売価格を計算します。

**リクエストボディ:**
```json
{
  "item_id": 1,
  "quantity": 10,
  "target_profit_rate": 0.2
}
```

**レスポンス例:**
```json
{
  "item_id": 1,
  "item_name": "高級素材",
  "quantity": 10,
  "current_lowest_price": 1000,
  "target_profit_rate": 20.0,
  "optimal_sell_price": 1263,
  "expected_profit": 2000,
  "actual_profit_rate": 20.0,
  "total_buy_cost": 10000,
  "total_revenue": 12630,
  "fee": 631
}
```

### GET /compare-margins

複数の価格帯での利益率を比較します。

**クエリパラメータ:**
- `item_id` (int, required): アイテムID
- `quantity` (int, optional): 数量（デフォルト: 1）

**レスポンス例:**
```json
{
  "item_id": 1,
  "item_name": "高級素材",
  "buy_price": 1000,
  "quantity": 10,
  "scenarios": [
    {
      "markup": "5%",
      "sell_price": 1050,
      "profit": -25,
      "profit_rate": -0.25
    },
    {
      "markup": "20%",
      "sell_price": 1200,
      "profit": 1400,
      "profit_rate": 14.0
    }
  ]
}
```

---

## エラーレスポンス

エラー時は適切なHTTPステータスコードとともに以下の形式で返されます:

```json
{
  "detail": "エラーメッセージ"
}
```

**主なステータスコード:**
- `200`: 成功
- `400`: 不正なリクエスト
- `404`: リソースが見つからない
- `422`: バリデーションエラー
- `500`: サーバーエラー

---

## レート制限

現在、レート制限は実装されていません。本番環境では適切なレート制限の実装を推奨します。

---

## インタラクティブなドキュメント

APIサーバー起動時に以下のURLでインタラクティブなドキュメントを参照できます:

- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
