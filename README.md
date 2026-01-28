# Star Resonance Japan Market Analyzer

ブループロトコル:スターレゾナンス の取引所解析ツール

## 概要

このツールは、ゲーム内の取引所データをパケット解析により取得し、市場価格の分析、損益計算、トレンド分析などを提供します。

**重要**: このツールはパケット解析のみを行い、ゲームクライアントへの干渉や改変は一切行いません。

## 機能

- 📊 **市場価格分析**: リアルタイムの取引所データを取得・保存
- 🔴 **リアルタイムキャプチャ**: ゲーム実行中にパケットを自動監視・記録
- 💰 **損益計算**: 取引の利益率を自動計算
- 📈 **価格履歴追跡**: アイテムごとの価格推移を記録
- 🌐 **Web UI**: ブラウザから市場データを閲覧
- 🤖 **REST API + WebSocket**: Discord Botなど外部ツールとの連携

## プロジェクト構成

```
StarResonance_Japan_Market_Analyzer/
├── src/                          # ソースコード
│   ├── packet_decoder/           # パケット解析
│   ├── database/                 # データベース
│   ├── analyzer/                 # 分析ツール
│   └── api/                      # REST API
├── web/                          # Webフロントエンド
├── docs/                         # ドキュメント
├── examples/                     # 使用例
├── scripts/                      # ユーティリティスクリプト
├── requirements.txt              # Python依存パッケージ
└── quick-install.bat             # ⭐ クイックインストール
```

## クイックスタート（5分で試せる！）

### 最速インストール

**ステップ1: Python バージョン確認**
```bat
check-python.bat
```

**ステップ2: インストール実行**

Python 3.10-3.11 の場合:
```bat
quick-install.bat
```

Python 3.12+ または エラーが出る場合:
```bat
install-minimal.bat
```

ブラウザで http://localhost:8000 にアクセスしてください！

## セットアップ

### 必要な環境

- **Python 3.10 または 3.11** (推奨)
  - Python 3.12+ は一部パッケージで互換性問題あり
  - Python 3.14+ は非対応
- PostgreSQL 14+ (または SQLite - 開発用)
- Wireshark (パケットキャプチャ用、オプション)

### インストール方法

#### 方法1: クイックインストール（推奨）

```bash
quick-install.bat
```

#### 方法2: 手動インストール

```bash
# 1. リポジトリをクローン
git clone https://github.com/coffin399/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer

# 2. 仮想環境を作成
python -m venv venv
venv\Scripts\activate

# 3. 依存パッケージをインストール
pip install --upgrade pip
pip install -r requirements.txt

# エラーが出る場合は個別にインストール
pip install sqlalchemy fastapi uvicorn[standard] pydantic alembic aiosqlite jinja2 python-dotenv websockets

# 4. データベースをセットアップ
python -m src.database.setup

# 5. サンプルデータをインポート（オプション）
python scripts/import_sample_data.py

# 6. APIサーバーを起動
python -m src.api.main
```

#### 方法3: Dockerを使用する場合

```bash
docker-compose up -d
```

### トラブルシューティング

**`psycopg2-binary` インストールエラー**

PostgreSQLは本番環境用です。開発環境ではSQLiteを使用するため不要です。

```bash
# PostgreSQL なしでインストール
pip install sqlalchemy fastapi uvicorn[standard] pydantic alembic aiosqlite jinja2 python-dotenv websockets
```

詳細は [INSTALL_GUIDE.md](INSTALL_GUIDE.md) を参照してください。

## 使い方

### 方法1: リアルタイムキャプチャ（推奨）

ゲーム実行中に自動でパケットをキャプチャし、データベースに保存します。

#### Pythonスクリプトで起動

```python
python examples/realtime_capture_example.py
```

#### API経由で制御

```bash
# キャプチャ開始
curl -X POST http://localhost:8000/api/v1/realtime/start

# ステータス確認
curl http://localhost:8000/api/v1/realtime/status

# キャプチャ停止
curl -X POST http://localhost:8000/api/v1/realtime/stop
```

#### WebSocketでリアルタイム受信

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'new_listings') {
        console.log('New listings:', data.listings);
    }
};
```

### 方法2: Wiresharkで手動キャプチャ（推奨）

既存のpcapファイルを専用パーサーで解析します。

#### 1. Wiresharkでキャプチャ

```
1. Wiresharkを起動
2. ネットワークインターフェースを選択
3. キャプチャ開始
4. ゲームで取引所を開く・操作
5. キャプチャ停止
6. File → Save As → capture.pcap
```

#### 2. 専用パーサーで解析

**最も簡単な方法:**
```bat
# pcapファイルをドラッグ&ドロップ
tools\parse-pcap.bat

# または直接指定
tools\parse-pcap.bat capture.pcap
```

**インタラクティブツール:**
```bat
tools\analyze-traffic.bat
```

**Python から直接:**
```python
from tools.packet_parser import GamePacketParser

parser = GamePacketParser('capture.pcap')
items = parser.parse()
parser.save_results()  # JSON出力
```

#### 3. データベースにインポート

```bash
python scripts\import_from_json.py parsed_items_20260128_123456.json
```

### 3. Web UIでデータを確認

APIサーバーが起動していれば、以下のURLでアクセス:

```
http://localhost:8000
```

### 4. APIエンドポイント

```bash
# 全アイテムの最新価格を取得
GET /api/v1/items

# 特定アイテムの価格履歴
GET /api/v1/items/{item_id}/history

# 損益計算
POST /api/v1/calculate-profit
{
  "buy_price": 1000,
  "sell_price": 1500,
  "quantity": 10
}
```

## Cloudflare Tunnel での公開

ポート開放せずに外部公開する場合:

```bash
# 1. Cloudflare Tunnelをインストール
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

# 2. トンネルを作成
cloudflared tunnel create bpsr-market

# 3. トンネルを起動
cloudflared tunnel --config config.yml run
```

詳細は [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md) を参照してください。

## Discord Bot連携

APIを使用してDiscord Botから市場データを取得できます:

```python
import requests

# 最新のアイテム価格を取得
response = requests.get('https://your-tunnel.trycloudflare.com/api/v1/items')
items = response.json()
```

## ドキュメント

詳細なドキュメントは `docs/` フォルダにあります:

- [インストールガイド](INSTALL_GUIDE.md) - ⭐ トラブルシューティング付き
- [はじめに](docs/GETTING_STARTED.md) - 初心者向けガイド
- [リアルタイムキャプチャ](docs/realtime-capture.md) - ⭐ リアルタイムパケット監視（推奨）
- [APIリファレンス](docs/api-reference.md) - API仕様
- [パケット解析ガイド](docs/packet-analysis.md) - パケットキャプチャと解析
- [Cloudflare Tunnel設定](docs/cloudflare-tunnel.md) - 外部公開の方法
- [アーキテクチャ](docs/ARCHITECTURE.md) - システム設計
- [コントリビューションガイド](CONTRIBUTING.md) - 貢献方法

## 参考資料

このプロジェクトは以下のリポジトリを参考にしています:

- [JordieB/bpsr_labs](https://github.com/JordieB/bpsr_labs) - パケットデコーダーの実装参考
- [winjwinj/bpsr-logs](https://github.com/winjwinj/bpsr-logs) - リアルタイムパケット監視の実装参考（WinDivert使用）

## ライセンス

MIT License

## 免責事項

このツールは教育・研究目的で提供されています。使用は自己責任でお願いします。
ゲーム運営の規約を遵守し、適切に使用してください。

## 貢献

プルリクエストを歓迎します！バグ報告や機能要望はIssueで受け付けています。
