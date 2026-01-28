# Python 3.10 インストールガイド

このプロジェクトは **Python 3.10.x** での動作を推奨しています。

## なぜ Python 3.10 なのか？

- ✅ **最も互換性が高い**: すべてのパッケージが安定動作
- ✅ **Pydantic のビルド不要**: バイナリホイールが利用可能
- ✅ **長期サポート**: 2026年10月までサポート
- ⚠️ Python 3.12+ は一部パッケージで問題あり
- ❌ Python 3.14+ は Pydantic が非対応

## インストール手順

### Windows

#### ステップ1: ダウンロード

**推奨バージョン: Python 3.10.11**

[公式ダウンロードページ](https://www.python.org/downloads/release/python-31011/)

または直接ダウンロード:
- [Windows installer (64-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
- [Windows installer (32-bit)](https://www.python.org/ftp/python/3.10.11/python-3.10.11.exe)

#### ステップ2: インストール

1. ダウンロードしたインストーラーを実行
2. **重要**: ☑ "Add Python 3.10 to PATH" にチェック
3. "Install Now" をクリック
4. インストール完了を待つ

#### ステップ3: 確認

コマンドプロンプトまたはPowerShellで:

```cmd
py -3.10 --version
```

出力例:
```
Python 3.10.11
```

### 既に他のバージョンがインストールされている場合

Python Launcher (`py`) が複数バージョンを管理します。

**利用可能なバージョンを確認:**
```cmd
py --list
```

**特定バージョンを使用:**
```cmd
py -3.10 --version
py -3.11 --version
```

プロジェクトのバッチファイルは自動的に最適なバージョンを選択します。

## インストール確認

### 方法1: チェックスクリプト実行

```cmd
check-python.bat
```

**期待される出力:**
```
========================================
Python Compatibility Check
========================================

Found Python:
Python 3.10.11

✓ Compatible

========================================
✓ Your Python version is PERFECT!
========================================
```

### 方法2: 手動確認

```cmd
REM バージョン確認
py -3.10 --version

REM pip 確認
py -3.10 -m pip --version

REM venv 確認
py -3.10 -m venv --help
```

すべて正常に動作すればOK！

## トラブルシューティング

### Q: "py: command not found"

**A:** Python Launcher がインストールされていません。

**解決策:**
1. Python を再インストール
2. インストール時に "Add Python to PATH" をチェック

### Q: Python 3.10 が見つからない

**A:** インストール後、コマンドプロンプトを再起動してください。

```cmd
REM 環境変数を更新
refreshenv

REM または、コマンドプロンプトを閉じて再起動
```

### Q: "Access is denied"

**A:** 管理者権限が必要な可能性があります。

**解決策:**
- インストーラーを右クリック → "管理者として実行"

### Q: 古いバージョンを削除したい

**A:** 設定から削除できます。

**手順:**
1. 設定 → アプリ → インストールされているアプリ
2. "Python 3.X" を検索
3. アンインストール

**注意:** 他のプログラムが使用している可能性があるため、確認してから削除してください。

## 複数バージョンの管理

### Python Launcher の使い方

```cmd
REM すべてのバージョンをリスト
py --list

REM 特定バージョンで実行
py -3.10 script.py
py -3.11 script.py

REM 最新の Python 3 を使用
py -3 script.py

REM デフォルトバージョンを使用
py script.py
```

### プロジェクトで使用するバージョン

このプロジェクトのバッチファイルは、以下の優先順位で Python を探します:

1. **Python 3.10.x** (最優先)
2. Python 3.11.x
3. Python 3 (最新)
4. `python` コマンド

## インストール後の次のステップ

### 1. プロジェクトのセットアップ

```cmd
REM Python バージョン確認
check-python.bat

REM インストール実行
quick-install.bat
```

### 2. サーバー起動

```cmd
start.bat
```

### 3. ブラウザでアクセス

```
http://localhost:8000
```

## 推奨設定

### VS Code / Cursor

`.vscode/settings.json` に追加:

```json
{
  "python.defaultInterpreterPath": "venv\\Scripts\\python.exe",
  "python.pythonPath": "venv\\Scripts\\python.exe"
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Virtualenv Environment
3. Existing environment → `venv\Scripts\python.exe`

## まとめ

| 項目 | 推奨 |
|------|------|
| バージョン | Python 3.10.11 |
| インストーラー | [64-bit版](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe) |
| PATH設定 | ✅ 必須 |
| 複数バージョン | ✅ 可能（Python Launcher使用） |

**確認コマンド:**
```cmd
check-python.bat
```

**インストールコマンド:**
```cmd
quick-install.bat
```

Python 3.10.11 をインストールすれば、すべてスムーズに動作します！🚀
