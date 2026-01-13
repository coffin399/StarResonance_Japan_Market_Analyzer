# Web API 設計書（将来実装予定）

## 概要

このドキュメントは、将来実装予定の損益計算サイト用Web APIの設計を記載します。

## アーキテクチャ

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Desktop   │─────▶│   Web API    │◀─────│  Web Client │
│   Client    │      │   (Rust)     │      │  (React/    │
│  (Tauri)    │      │              │      │   Vue/etc)  │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     │
       │                     │
       ▼                     ▼
┌─────────────┐      ┌──────────────┐
│  Local DB   │      │  PostgreSQL  │
│  (SQLite)   │      │              │
└─────────────┘      └──────────────┘
```

## エンドポイント設計

### 認証

#### `POST /api/auth/register`
ユーザー登録

**Request:**
```json
{
  "username": "player123",
  "email": "player@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "user_id": "uuid",
  "token": "jwt_token"
}
```

#### `POST /api/auth/login`
ログイン

#### `POST /api/auth/logout`
ログアウト

### 市場データ

#### `GET /api/market/items`
アイテム一覧取得

**Query Parameters:**
- `page`: ページ番号（デフォルト: 1）
- `limit`: 1ページあたりのアイテム数（デフォルト: 50）
- `category`: カテゴリフィルタ
- `search`: 検索キーワード
- `sort`: ソート順（price_asc, price_desc, name_asc, name_desc, updated_desc）

**Response:**
```json
{
  "items": [
    {
      "id": "item_001",
      "name": "レア武器",
      "current_price": 150000,
      "average_price_7d": 145000,
      "price_change_percent": 3.4,
      "category": "weapon",
      "rarity": 5,
      "last_updated": "2026-01-13T10:30:00Z"
    }
  ],
  "total": 1500,
  "page": 1,
  "pages": 30
}
```

#### `GET /api/market/items/:id`
特定アイテムの詳細情報

**Response:**
```json
{
  "id": "item_001",
  "name": "レア武器",
  "description": "強力な武器",
  "current_price": 150000,
  "statistics": {
    "avg_price_24h": 148000,
    "avg_price_7d": 145000,
    "avg_price_30d": 140000,
    "min_price_7d": 130000,
    "max_price_7d": 160000,
    "volatility": 0.15
  },
  "category": "weapon",
  "rarity": 5
}
```

#### `GET /api/market/items/:id/history`
アイテムの価格履歴

**Query Parameters:**
- `period`: 期間（24h, 7d, 30d, 90d, all）
- `interval`: データポイントの間隔（1h, 6h, 1d）

**Response:**
```json
{
  "item_id": "item_001",
  "period": "7d",
  "data": [
    {
      "timestamp": "2026-01-06T00:00:00Z",
      "price": 140000,
      "volume": 25
    },
    {
      "timestamp": "2026-01-07T00:00:00Z",
      "price": 142000,
      "volume": 30
    }
  ]
}
```

### 損益計算

#### `POST /api/calculator/profit`
損益計算

**Request:**
```json
{
  "transactions": [
    {
      "item_id": "item_001",
      "type": "buy",
      "quantity": 5,
      "price_per_unit": 140000,
      "timestamp": "2026-01-10T10:00:00Z"
    },
    {
      "item_id": "item_001",
      "type": "sell",
      "quantity": 3,
      "price_per_unit": 150000,
      "timestamp": "2026-01-12T15:00:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "summary": {
    "total_invested": 700000,
    "total_revenue": 450000,
    "net_profit": -250000,
    "roi_percent": -35.7,
    "holding_value": 300000
  },
  "by_item": [
    {
      "item_id": "item_001",
      "item_name": "レア武器",
      "bought": 5,
      "sold": 3,
      "holding": 2,
      "avg_buy_price": 140000,
      "avg_sell_price": 150000,
      "realized_profit": 30000,
      "unrealized_profit": 20000,
      "total_profit": 50000
    }
  ]
}
```

#### `GET /api/calculator/portfolio`
ユーザーのポートフォリオ

**Response:**
```json
{
  "user_id": "uuid",
  "total_value": 5000000,
  "holdings": [
    {
      "item_id": "item_001",
      "item_name": "レア武器",
      "quantity": 10,
      "avg_buy_price": 140000,
      "current_price": 150000,
      "total_value": 1500000,
      "profit_loss": 100000,
      "profit_loss_percent": 7.14
    }
  ],
  "performance": {
    "total_profit": 500000,
    "roi_percent": 11.1,
    "best_performing": {
      "item_id": "item_002",
      "profit_percent": 50.0
    },
    "worst_performing": {
      "item_id": "item_003",
      "profit_percent": -20.0
    }
  }
}
```

### データ共有

#### `POST /api/data/upload`
ローカルデータのアップロード（デスクトップクライアントから）

**Request:**
```json
{
  "user_token": "jwt_token",
  "data": [
    {
      "item_id": "item_001",
      "price": 150000,
      "quantity": 5,
      "timestamp": "2026-01-13T10:30:00Z",
      "server": "JP-1"
    }
  ]
}
```

**Response:**
```json
{
  "uploaded": 1,
  "rejected": 0,
  "message": "データが正常にアップロードされました"
}
```

#### `GET /api/stats/global`
グローバル統計

**Response:**
```json
{
  "total_users": 5000,
  "total_items_tracked": 1500,
  "total_transactions": 50000,
  "data_points_last_24h": 100000,
  "most_traded_items": [
    {
      "item_id": "item_001",
      "item_name": "レア武器",
      "trade_volume_24h": 500
    }
  ]
}
```

## データモデル

### User
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);
```

### MarketItem
```sql
CREATE TABLE market_items (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    rarity INTEGER,
    icon_url VARCHAR(255)
);
```

### PriceData
```sql
CREATE TABLE price_data (
    id BIGSERIAL PRIMARY KEY,
    item_id VARCHAR(50) REFERENCES market_items(id),
    price BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    server VARCHAR(50),
    user_id UUID REFERENCES users(id),
    recorded_at TIMESTAMP NOT NULL,
    INDEX idx_item_recorded (item_id, recorded_at),
    INDEX idx_recorded_at (recorded_at)
);
```

### Transaction
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    item_id VARCHAR(50) REFERENCES market_items(id),
    type VARCHAR(10) NOT NULL, -- 'buy' or 'sell'
    quantity INTEGER NOT NULL,
    price_per_unit BIGINT NOT NULL,
    total_amount BIGINT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    notes TEXT
);
```

### Portfolio
```sql
CREATE TABLE portfolio (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    item_id VARCHAR(50) REFERENCES market_items(id),
    quantity INTEGER NOT NULL,
    avg_buy_price BIGINT NOT NULL,
    last_updated TIMESTAMP NOT NULL,
    UNIQUE(user_id, item_id)
);
```

## セキュリティ

### 認証
- JWT（JSON Web Token）による認証
- トークンの有効期限: 24時間
- リフレッシュトークン機能

### レート制限
- 一般ユーザー: 100リクエスト/分
- 認証済みユーザー: 300リクエスト/分
- データアップロード: 1000リクエスト/時

### データ検証
- すべての入力データのバリデーション
- SQLインジェクション対策
- XSS対策

## 技術スタック（予定）

### バックエンド
- **言語**: Rust
- **Webフレームワーク**: Axum または Actix-web
- **データベース**: PostgreSQL
- **キャッシュ**: Redis
- **認証**: jsonwebtoken
- **ORM/クエリビルダー**: SQLx または Diesel

### インフラ
- **ホスティング**: AWS / GCP / Azure
- **コンテナ**: Docker
- **CI/CD**: GitHub Actions
- **モニタリング**: Prometheus + Grafana

### フロントエンド（Webサイト）
- **フレームワーク**: Next.js / Svelte / Vue.js
- **チャート**: Chart.js / Recharts
- **状態管理**: Zustand / Pinia
- **UIライブラリ**: TailwindCSS / shadcn/ui

## デプロイメント戦略

### Phase 1: ベータ版
- 限定ユーザーでのテスト
- データ収集の安定性確認
- フィードバック収集

### Phase 2: パブリックアルファ
- 一般公開
- コミュニティからのデータ収集
- スケーラビリティの検証

### Phase 3: 正式リリース
- すべての機能を有効化
- 有料プランの導入（オプション）
- モバイルアプリの検討

## 今後の機能

- [ ] リアルタイム価格通知
- [ ] 価格予測（機械学習）
- [ ] トレード推奨機能
- [ ] Discord/LINEボット
- [ ] モバイルアプリ
- [ ] API公開（サードパーティ開発者向け）
- [ ] マルチサーバー対応
- [ ] 多言語対応
