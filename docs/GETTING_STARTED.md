# はじめに - Getting Started

このガイドでは、Star Resonance Market Analyzer を初めて使う方向けに、セットアップから基本的な使い方までを説明します。

## 📋 目次

1. [システム要件](#システム要件)
2. [インストール](#インストール)
3. [初回セットアップ](#初回セットアップ)
4. [基本的な使い方](#基本的な使い方)
5. [よくある質問](#よくある質問)

---

## システム要件

### 最小要件

- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.10以上
- **RAM**: 4GB以上
- **ストレージ**: 1GB以上の空き容量

### 推奨環境

- **OS**: Windows 11
- **Python**: 3.11
- **RAM**: 8GB以上
- **ストレージ**: 5GB以上の空き容量
- **Wireshark**: 最新版（パケットキャプチャ用）

---

## インストール

### 方法1: 簡単スタート（推奨）

Windows の場合、`start.bat` をダブルクリックするだけで自動的にセットアップが完了します。

```bash
# start.bat をダブルクリック
```

Linux/macOS の場合:

```bash
chmod +x start.sh
./start.sh
```

### 方法2: 手動インストール

#### ステップ1: Pythonのインストール確認

```bash
python --version
```

Python 3.10以上が必要です。インストールされていない場合は [python.org](https://www.python.org/downloads/) からダウンロードしてください。

#### ステップ2: リポジトリのクローン

```bash
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer
```

#### ステップ3: 仮想環境の作成

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### ステップ4: 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

---

## 初回セットアップ

### 1. データベースの初期化

```bash
python -m src.database.setup
```

これで SQLite データベースファイル `bpsr_market.db` が作成されます。

### 2. サンプルデータのインポート（オプション）

動作確認用にサンプルデータをインポートできます:

```bash
python scripts/import_sample_data.py
```

これにより以下が作成されます:
- 10種類のアイテム
- 各アイテムの出品情報（5-15件）
- 30日分の価格履歴

### 3. 環境変数の設定（本番環境）

`.env.example` をコピーして `.env` を作成:

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

`.env` ファイルを編集して、必要な設定を行います:

```env
# SQLiteを使う場合（開発用）
DATABASE_URL=sqlite:///./bpsr_market.db

# PostgreSQLを使う場合（本番用）
# DATABASE_URL=postgresql://user:password@localhost:5432/bpsr_market

# APIサーバー設定
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here-change-this
```

---

## 基本的な使い方

### APIサーバーの起動

```bash
python -m src.api.main
```

サーバーが起動したら、ブラウザで以下にアクセス:

```
http://localhost:8000
```

### Web UI の主な機能

#### 1. 市場概要

トップページで以下の情報を確認できます:
- アクティブな出品数
- ユニークアイテム数
- 総出品額
- 24時間の新規出品数

#### 2. トレンドアイテム

最近活発に取引されているアイテムを一覧で表示。

#### 3. 出品情報の検索

アイテム名で検索して、現在の出品状況を確認できます。

#### 4. 損益計算ツール

取引の利益を簡単に計算:
1. 購入価格を入力
2. 販売価格を入力
3. 数量を入力
4. 「計算する」をクリック

純利益、利益率、ROIが自動で計算されます。

### API の使用

#### インタラクティブなドキュメント

Swagger UI で API を試せます:

```
http://localhost:8000/api/docs
```

#### 基本的なAPI呼び出し例

Python:
```python
import requests

# 最新の出品を取得
response = requests.get('http://localhost:8000/api/v1/listings/latest/all')
listings = response.json()

for listing in listings[:5]:
    print(f"{listing['item_name']}: {listing['price']}円")
```

cURL:
```bash
# トレンドアイテムを取得
curl http://localhost:8000/api/v1/listings/trending?hours=24&limit=10
```

---

## パケットキャプチャの実施

### 1. Wiresharkのインストール

[Wireshark公式サイト](https://www.wireshark.org/download.html) からダウンロードしてインストール。

### 2. キャプチャの開始

1. Wiresharkを起動
2. 使用しているネットワークインターフェースを選択
3. キャプチャを開始
4. ゲームを起動して取引所にアクセス
5. いくつかの操作を行う
6. キャプチャを停止

### 3. Pcapファイルの保存

File → Save As → `pcaps/trading_capture.pcap`

### 4. パケットの解析

```python
from src.packet_decoder import TradingCenterDecoder

decoder = TradingCenterDecoder('pcaps/trading_capture.pcap')
packets = decoder.decode_pcap_file()

print(f"デコードしたパケット数: {len(packets)}")
```

詳細は [パケット解析ガイド](packet-analysis.md) を参照してください。

---

## よくある質問

### Q: データベースファイルはどこに保存されますか？

A: プロジェクトのルートディレクトリに `bpsr_market.db` として保存されます。

### Q: ポート8000が既に使用されている場合は？

A: `.env` ファイルで `API_PORT` を変更してください:

```env
API_PORT=8080
```

### Q: サンプルデータを削除したい

A: データベースを再作成してください:

```bash
# データベースファイルを削除
rm bpsr_market.db  # Linux/macOS
del bpsr_market.db  # Windows

# 再作成
python -m src.database.setup
```

### Q: 本番環境でPostgreSQLを使いたい

A: Docker Composeを使用するのが簡単です:

```bash
docker-compose up -d
```

または手動でPostgreSQLをセットアップして、`.env` の `DATABASE_URL` を変更してください。

### Q: Cloudflare Tunnelの設定方法は？

A: [Cloudflare Tunnel設定ガイド](cloudflare-tunnel.md) を参照してください。

### Q: Discord Botと連携したい

A: APIを使用してDiscord Botからデータを取得できます。詳細は [APIリファレンス](api-reference.md) を参照してください。

---

## 次のステップ

基本的なセットアップが完了したら、以下のドキュメントも参照してください:

- [APIリファレンス](api-reference.md) - API の詳細な使い方
- [パケット解析ガイド](packet-analysis.md) - パケットキャプチャと解析の詳細
- [Cloudflare Tunnel設定](cloudflare-tunnel.md) - 外部公開の方法
- [コントリビューションガイド](../CONTRIBUTING.md) - プロジェクトへの貢献方法

---

## サポート

問題が発生した場合:

1. [よくある質問](#よくある質問) を確認
2. GitHub Issues で検索
3. 新しいIssueを作成

貢献やフィードバックは常に歓迎します！
