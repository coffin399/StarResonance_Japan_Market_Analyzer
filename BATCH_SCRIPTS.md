# バッチファイル使用ガイド

Windows用の便利なバッチファイルを用意しました。

## 📁 バッチファイル一覧

### 🚀 開発用

#### `start-dev-auto-admin.bat` ⭐ おすすめ
**自動的に管理者権限で開発サーバーを起動**

```batch
start-dev-auto-admin.bat
```

- ダブルクリックで実行
- 管理者権限がない場合は自動的に昇格
- 依存関係を自動確認
- WinDivertファイルをチェック
- 開発サーバーを起動

#### `start-dev.bat`
**管理者権限で開発サーバーを起動**（手動昇格）

```batch
# 右クリック → 「管理者として実行」
start-dev.bat
```

- 管理者権限のチェック
- Node.js / Rust の確認
- 依存関係のインストール確認
- WinDivertファイルの確認
- 開発サーバー起動

### 🏗️ ビルド用

#### `build.bat`
**リリースビルドを作成**

```batch
build.bat
```

- 最適化されたバイナリを生成
- MSIインストーラーを作成
- 成果物の場所を表示

**成果物の場所:**
```
src-tauri\target\release\
  ├── StarResonance-Market-Analyzer.exe  (実行ファイル)
  └── bundle\msi\                         (インストーラー)
```

### ▶️ 実行用

#### `run.bat`
**ビルド済みアプリを管理者権限で実行**

```batch
run.bat
```

- 管理者権限で自動昇格
- ビルド済みの実行ファイルを起動

### 🧹 メンテナンス用

#### `clean.bat`
**ビルドキャッシュをクリーンアップ**

```batch
clean.bat
```

削除されるもの:
- `node_modules/`
- `src-tauri/target/`
- `.svelte-kit/`
- `build/`

**使用タイミング:**
- ビルドエラーが解決しない時
- 依存関係を再インストールしたい時
- ディスク容量を節約したい時

## 🎯 使い方の例

### 初めて開発を始める

```batch
# 1. 自動管理者権限で開発サーバー起動
start-dev-auto-admin.bat

# アプリが起動したら:
# - 「監視開始」ボタンをクリック
# - ゲームを起動して取引所を開く
```

### リリース版をビルド

```batch
# 1. ビルド
build.bat

# 2. 実行
run.bat
```

### トラブル時

```batch
# 1. クリーンアップ
clean.bat

# 2. 再度開発サーバー起動
start-dev-auto-admin.bat
```

## ⚙️ バッチファイルの詳細

### start-dev-auto-admin.bat の動作

```
起動
  ↓
管理者権限チェック
  ↓ No
管理者として再起動 ━━━┓
  ↓ Yes              ↓
start-dev.bat を実行 ←┛
  ↓
環境チェック
  ↓
開発サーバー起動
```

### build.bat の動作

```
起動
  ↓
環境チェック
  ↓
依存関係確認
  ↓
WinDivertファイル確認
  ↓
npm run tauri build
  ↓
ビルド完了
  ↓
成果物の場所を表示
```

### clean.bat の動作

```
起動
  ↓
削除内容を表示
  ↓
確認プロンプト
  ↓ Yes
ファイル削除
  ↓
完了
```

## 🔧 カスタマイズ

### 環境変数の追加

`start-dev.bat` を編集して環境変数を設定:

```batch
:: 環境変数の設定
set RUST_LOG=debug
set RUST_BACKTRACE=1

:: 開発サーバー起動
npm run tauri dev
```

### ポート番号の変更

`vite.config.ts` でポートを変更:

```typescript
export default defineConfig({
  server: {
    port: 3000  // お好みのポートに変更
  }
});
```

### ビルド最適化

`src-tauri/Cargo.toml` に最適化設定:

```toml
[profile.release]
opt-level = "z"     # サイズ最適化
lto = true          # リンク時最適化
codegen-units = 1   # 最大最適化
strip = true        # デバッグ情報削除
```

## 📝 トラブルシューティング

### "npm が認識されません"

**原因**: Node.js がインストールされていない、またはPATHが通っていない

**解決策**:
1. https://nodejs.org/ からNode.jsをダウンロード
2. インストール後、コマンドプロンプトを再起動

### "cargo が認識されません"

**原因**: Rust がインストールされていない

**解決策**:
1. https://rustup.rs/ からRustをインストール
2. コマンドプロンプトを再起動

### "WinDivert64.dll が見つかりません"

**原因**: WinDivertファイルが配置されていない

**解決策**:
`src-tauri/README_WINDIVERT.md` を参照してください

### "管理者権限が必要です"

**原因**: 管理者権限で実行されていない

**解決策**:
- `start-dev-auto-admin.bat` を使用（自動昇格）
- または右クリック → 「管理者として実行」

## 💡 Tips

### 開発効率化

1. **ショートカット作成**
   ```
   start-dev-auto-admin.bat を右クリック
   → 送る → デスクトップ (ショートカットを作成)
   ```

2. **タスクバーにピン留め**
   - ショートカットをタスクバーにドラッグ

3. **キーボードショートカット設定**
   - ショートカットを右クリック → プロパティ
   - ショートカットキーを設定（例: Ctrl+Alt+S）

### ログ出力

開発時のログをファイルに保存:

```batch
npm run tauri dev > dev.log 2>&1
```

### 並行開発

複数のターミナルで:

```batch
# ターミナル1: フロントエンド
npm run dev

# ターミナル2: バックエンド
cd src-tauri
cargo build --release
```

## 🔗 関連ドキュメント

- [README.md](README.md) - プロジェクト概要
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - 開発ガイド
- [QUICKSTART.md](QUICKSTART.md) - クイックスタート
- [INSTALLATION.md](INSTALLATION.md) - インストールガイド

---

**ヒント**: 一番簡単なのは `start-dev-auto-admin.bat` をダブルクリックするだけ！
