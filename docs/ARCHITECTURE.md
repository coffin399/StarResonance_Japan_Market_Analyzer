# アーキテクチャ概要

Star Resonance Market Analyzer のシステムアーキテクチャと設計思想について説明します。

## システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                        User Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Web Browser  │  Discord Bot  │  External Tools             │
└────────┬──────┴──────┬────────┴─────────────────────────────┘
         │             │
         v             v
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
├─────────────────────────────────────────────────────────────┤
│  REST API  │  WebSocket (Future)  │  Authentication         │
└────────┬────────────────────────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Profit Analyzer  │  Trend Analyzer  │  Statistics          │
└────────┬────────────────────────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                               │
├─────────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM  │  Database Models  │  Migrations          │
└────────┬────────────────────────────────────────────────────┘
         │
         v
┌─────────────────────────────────────────────────────────────┐
│                  Storage Layer                              │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL / SQLite  │  File Storage  │  Cache (Future)    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Packet Capture & Decode (Offline)              │
├─────────────────────────────────────────────────────────────┤
│  Wireshark  │  Packet Decoder  │  Data Import               │
└─────────────────────────────────────────────────────────────┘
```

## モジュール構成

### 1. パケットデコーダー (`src/packet_decoder/`)

**責務**: ゲームのネットワークパケットを解析し、取引所データを抽出

```
packet_decoder/
├── __init__.py
├── decoder.py           # メインのデコーダークラス
└── packet_types.py      # パケットのデータ構造定義
```

**主要クラス**:
- `TradingCenterDecoder`: Pcapファイルまたはバイト列からパケットをデコード
- `TradingPacket`: デコードされたパケット情報
- `ItemListing`: アイテムの出品情報
- `MarketSnapshot`: 市場の瞬間的な状態

**技術スタック**:
- Scapy: パケット解析
- struct: バイナリデータの解析

### 2. データベース (`src/database/`)

**責務**: データの永続化とクエリ

```
database/
├── __init__.py
├── connection.py        # データベース接続管理
├── models.py            # SQLAlchemyモデル
└── setup.py             # データベース初期化
```

**主要モデル**:
- `Item`: アイテム情報
- `Listing`: 出品情報
- `PriceHistory`: 価格履歴
- `Transaction`: 取引履歴
- `MarketStatistics`: 市場統計

**技術スタック**:
- SQLAlchemy: ORM
- Alembic: マイグレーション（将来実装）
- PostgreSQL/SQLite: データベース

### 3. 分析ツール (`src/analyzer/`)

**責務**: 市場データの分析と洞察の提供

```
analyzer/
├── __init__.py
├── profit_analyzer.py   # 損益計算ツール
└── trend_analyzer.py    # トレンド分析ツール
```

**主要機能**:
- 利益計算
- 損益分岐点の算出
- 価格トレンド分析
- ボラティリティ計算
- サポート・レジスタンスの特定

**技術スタック**:
- Python標準ライブラリ (statistics)
- NumPy/Pandas（将来拡張）

### 4. API (`src/api/`)

**責務**: RESTful APIの提供

```
api/
├── __init__.py
├── main.py              # FastAPIアプリケーション
├── schemas.py           # Pydanticスキーマ
└── routes/
    ├── __init__.py
    ├── items.py         # アイテム関連
    ├── listings.py      # 出品情報関連
    ├── statistics.py    # 統計情報
    └── profit_calculator.py  # 損益計算
```

**エンドポイントグループ**:
- `/api/v1/items`: アイテム情報
- `/api/v1/listings`: 出品情報
- `/api/v1/statistics`: 統計情報
- `/api/v1/calculate-profit`: 損益計算

**技術スタック**:
- FastAPI: Webフレームワーク
- Pydantic: データバリデーション
- Uvicorn: ASGIサーバー

### 5. Webフロントエンド (`web/`)

**責務**: ユーザーインターフェースの提供

```
web/
├── templates/
│   └── index.html       # メインページ
└── static/
    ├── css/
    │   └── style.css    # スタイルシート
    └── js/
        └── main.js      # フロントエンドロジック
```

**機能**:
- 市場概要ダッシュボード
- トレンドアイテム表示
- 出品情報検索
- 損益計算ツール

**技術スタック**:
- HTML5/CSS3
- Vanilla JavaScript
- Chart.js（将来実装）

## データフロー

### パケットキャプチャからデータベースまで

```
[Wireshark] → [.pcap file]
     ↓
[TradingCenterDecoder]
     ↓
[TradingPacket objects]
     ↓
[Database (SQLAlchemy)]
     ↓
[PostgreSQL/SQLite]
```

### APIリクエストの処理

```
[Client Request] → [FastAPI Router]
     ↓
[Route Handler]
     ↓
[Database Query (SQLAlchemy)]
     ↓
[Pydantic Schema (Validation)]
     ↓
[JSON Response]
```

## 設計原則

### 1. 分離されたレイヤー

各レイヤーは明確な責務を持ち、他のレイヤーから独立しています。

### 2. 依存性注入

FastAPIの依存性注入を使用してデータベースセッションを管理。

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/items")
async def get_items(db: Session = Depends(get_db)):
    # ...
```

### 3. 型安全性

Pydanticと型ヒントを使用して型安全性を確保。

```python
class ItemResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
```

### 4. 非同期処理

FastAPIの非同期機能を活用して高いパフォーマンスを実現。

```python
@router.get("/items")
async def get_items(...):
    # 非同期処理
```

### 5. エラーハンドリング

適切なHTTPステータスコードとエラーメッセージを返す。

```python
if not item:
    raise HTTPException(status_code=404, detail="Item not found")
```

## スケーラビリティ

### 水平スケーリング

- ステートレスなAPI設計
- データベース接続プーリング
- ロードバランサーによる分散

### 垂直スケーリング

- データベースインデックスの最適化
- クエリのパフォーマンスチューニング
- キャッシュの実装（将来）

### 将来の拡張

- **Redis**: キャッシュとセッション管理
- **WebSocket**: リアルタイムデータ配信
- **Celery**: バックグラウンドタスク処理
- **Elasticsearch**: 高速な全文検索

## セキュリティ

### 現在の実装

- CORS設定
- 入力バリデーション（Pydantic）
- SQLインジェクション対策（SQLAlchemy ORM）

### 将来の実装

- JWT認証
- レート制限
- APIキー認証
- ロギングと監視

## パフォーマンス最適化

### データベース

```python
# インデックスの使用
__table_args__ = (
    Index("idx_item_status_captured", "item_id", "status", "captured_at"),
)
```

### クエリ最適化

```python
# Eager LoadingでN+1問題を回避
items = db.query(Item).options(
    joinedload(Item.listings)
).all()
```

### ページネーション

```python
@router.get("/items")
async def get_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items
```

## テスト戦略

### ユニットテスト

- `pytest`を使用
- 各モジュールの独立したテスト
- モックとフィクスチャの活用

### 統合テスト

- APIエンドポイントのテスト
- データベース操作のテスト

### テストカバレッジ

```bash
pytest --cov=src tests/
```

## デプロイメント

### Docker

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
  postgres:
    image: postgres:16-alpine
```

### Cloudflare Tunnel

ポート開放なしで外部公開可能。

## 監視とロギング

### ロギング

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### メトリクス（将来実装）

- Prometheus
- Grafana
- アプリケーションメトリクス

## まとめ

このアーキテクチャは以下を目指しています:

- **保守性**: クリーンで理解しやすいコード
- **拡張性**: 新機能の追加が容易
- **パフォーマンス**: 効率的なデータ処理
- **セキュリティ**: 安全なデータ管理
- **テスタビリティ**: 包括的なテストカバレッジ
