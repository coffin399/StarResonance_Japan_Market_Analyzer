# Installation Guide - インストールガイド

## Quick Start (最速インストール)

### Windows

```bat
quick-install.bat
```

このスクリプトを実行するだけで、すべてのセットアップが完了します。

---

## Manual Installation (手動インストール)

### Step 1: Python のインストール確認

```bash
python --version
```

Python 3.10以上が必要です。インストールされていない場合:
https://www.python.org/downloads/

### Step 2: 仮想環境の作成

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: 依存パッケージのインストール

#### Option A: 基本インストール（SQLite のみ）

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**エラーが出る場合:**

```bash
# Core packages first
pip install sqlalchemy fastapi uvicorn[standard] pydantic pydantic-settings

# Database
pip install alembic aiosqlite

# Data processing
pip install pandas numpy

# API utilities
pip install python-multipart jinja2 aiofiles python-dotenv

# WebSocket
pip install websockets
```

#### Option B: 本番環境（PostgreSQL 付き）

```bash
pip install -r requirements-prod.txt
```

**注意**: PostgreSQL のインストールが必要です。

### Step 4: データベースのセットアップ

```bash
python -m src.database.setup
```

### Step 5: サンプルデータのインポート（オプション）

```bash
python scripts/import_sample_data.py
```

### Step 6: サーバーの起動

```bash
python -m src.api.main
```

ブラウザで http://localhost:8000 にアクセス！

---

## Troubleshooting (トラブルシューティング)

### Error: `psycopg2-binary` installation failed

**原因**: PostgreSQL 関連のパッケージで、SQLite を使う場合は不要です。

**解決策**:
```bash
# requirements.txt から psycopg2-binary を削除
# または以下を実行
pip install sqlalchemy fastapi uvicorn[standard] pydantic alembic aiosqlite pandas numpy jinja2 python-dotenv websockets
```

### Error: `pydantic-core` build failed

**原因**: Python のバージョンが新しすぎる（3.14+）、または Rust コンパイラがない。

**解決策1: Python バージョンを確認**
```bash
check-python.bat
```

推奨: Python 3.10 または 3.11

**解決策2: 最小限インストール**
```bash
install-minimal.bat
```

**解決策3: 古いバージョンの pydantic を使用**
```bash
pip install "pydantic<2.0"
```

### Error: `ModuleNotFoundError: No module named 'sqlalchemy'`

**原因**: 依存パッケージがインストールされていません。

**解決策**:
```bash
pip install sqlalchemy
```

または一括インストール:
```bash
quick-install.bat
```

### Error: `scapy` installation failed

**原因**: Scapy は Npcap が必要です。

**解決策**:
- Scapy はパケットキャプチャにのみ必要
- 必要ない場合はスキップ可能
- 必要な場合は Wireshark をインストール（Npcap が含まれる）

```bash
# Scapy なしでインストール
pip install sqlalchemy fastapi uvicorn[standard] pydantic alembic aiosqlite
```

### Error: Permission denied

**原因**: 仮想環境の有効化に失敗しています。

**解決策**:
```bash
# PowerShell の場合
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# その後
venv\Scripts\activate
```

---

## Dependencies Overview (依存関係の概要)

### 必須パッケージ

- **FastAPI**: Web フレームワーク
- **SQLAlchemy**: ORM
- **Uvicorn**: ASGI サーバー
- **Pydantic**: データバリデーション
- **Aiosqlite**: SQLite 非同期サポート

### オプションパッケージ

- **Scapy**: パケットキャプチャ（Wireshark の代替）
- **psycopg2-binary**: PostgreSQL サポート（本番環境用）
- **Pandas/NumPy**: 高度な分析（将来の機能用）

### 開発用パッケージ

- **Pytest**: テスト
- **Black**: コードフォーマッタ
- **Flake8**: リンター

---

## Alternative Installation Methods

### Using pip directly (pip で直接インストール)

```bash
# Minimal installation (最小構成)
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic jinja2 python-dotenv

# Start server (サーバー起動)
python -m src.api.main
```

### Using Docker (Docker を使用)

```bash
docker-compose up -d
```

Docker を使用する場合、Python やパッケージのインストールは不要です。

---

## Verification (動作確認)

### 1. Import test

```bash
python -c "from src.database import SessionLocal; print('OK')"
```

### 2. API test

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"ok","version":"1.0.0"}
```

### 3. Web UI test

ブラウザで http://localhost:8000 にアクセスして、UI が表示されることを確認。

---

## Next Steps (次のステップ)

1. **サンプルデータで試す**
   ```bash
   python scripts/import_sample_data.py
   ```

2. **API ドキュメントを見る**
   ```
   http://localhost:8000/api/docs
   ```

3. **パケットキャプチャを試す** (オプション)
   ```bash
   python examples/realtime_capture_example.py
   ```

---

## Support (サポート)

問題が解決しない場合:

1. GitHub Issues で検索
2. 新しい Issue を作成
3. Discord サーバーで質問（準備中）

---

## Summary (まとめ)

### 最速インストール
```bash
quick-install.bat
```

### 手動インストール
```bash
python -m venv venv
venv\Scripts\activate
pip install sqlalchemy fastapi uvicorn[standard] pydantic alembic aiosqlite jinja2 python-dotenv websockets
python -m src.database.setup
python -m src.api.main
```

### Docker インストール
```bash
docker-compose up -d
```

どの方法でも、最終的に http://localhost:8000 でアクセスできます！
