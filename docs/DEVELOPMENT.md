# 開発ガイド

## 開発環境のセットアップ

### 必要なツール

1. **Node.js** (v18以上)
   ```bash
   # バージョン確認
   node --version
   npm --version
   ```

2. **Rust** (最新安定版)
   ```bash
   # Rustのインストール
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # バージョン確認
   rustc --version
   cargo --version
   ```

3. **Tauri CLI**
   ```bash
   # Tauri CLIのインストール
   cargo install tauri-cli
   ```

4. **Visual Studio Build Tools** (Windows)
   - [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
   - "Desktop development with C++" をインストール

### プロジェクトのセットアップ

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer

# 依存関係のインストール
npm install

# Rustの依存関係をビルド（初回のみ時間がかかります）
cd src-tauri
cargo build
cd ..
```

## 開発ワークフロー

### 開発サーバーの起動

```bash
# フロントエンドとバックエンドを同時に起動
npm run tauri:dev
```

このコマンドで以下が起動します:
- Vite開発サーバー (ホットリロード対応)
- Tauriアプリケーション (Rustバックエンド)

### コードの変更を監視

- **フロントエンド**: Svelteファイルの変更は自動でリロードされます
- **バックエンド**: Rustファイルの変更は保存時に自動で再コンパイルされます

### デバッグ

#### フロントエンドのデバッグ

```javascript
// ブラウザの開発者ツールと同じ
console.log('Debug message');
console.error('Error message');
```

Tauriウィンドウ内で右クリック → "Inspect Element" で開発者ツールを開けます。

#### バックエンドのデバッグ

```rust
use tracing::{info, debug, warn, error};

info!("情報メッセージ");
debug!("デバッグメッセージ");
warn!("警告メッセージ");
error!("エラーメッセージ");
```

ログはコンソールに出力されます。

### テスト

```bash
# フロントエンドのテスト
npm test

# バックエンドのテスト
cd src-tauri
cargo test
```

## プロジェクト構造

```
StarResonance_Japan_Market_Analyzer/
├── src/                    # Svelteフロントエンド
│   ├── routes/            # SvelteKitのルート
│   │   ├── +layout.svelte # 共通レイアウト
│   │   └── +page.svelte   # メインページ
│   ├── lib/               # 共有コンポーネント・ユーティリティ
│   ├── app.html           # HTMLテンプレート
│   └── app.css            # グローバルスタイル
│
├── src-tauri/             # Rustバックエンド
│   ├── src/
│   │   ├── main.rs        # エントリーポイント
│   │   ├── packet_capture.rs  # パケット傍受
│   │   ├── packet_parser.rs   # パケット解析
│   │   ├── database.rs    # データベース操作
│   │   └── models.rs      # データモデル
│   ├── Cargo.toml         # Rust依存関係
│   └── tauri.conf.json    # Tauri設定
│
├── docs/                  # ドキュメント
│   ├── API_DESIGN.md     # Web API設計
│   ├── PACKET_ANALYSIS.md # パケット解析ガイド
│   └── DEVELOPMENT.md    # 開発ガイド（このファイル）
│
├── package.json          # Node.js依存関係
├── vite.config.ts        # Vite設定
├── svelte.config.js      # Svelte設定
└── README.md             # プロジェクトREADME
```

## コーディング規約

### Rust

```rust
// 構造体名: PascalCase
pub struct MarketItem {
    // フィールド名: snake_case
    pub item_id: String,
    pub item_name: String,
}

// 関数名: snake_case
pub fn parse_packet(data: &[u8]) -> Result<MarketPacket> {
    // 定数: SCREAMING_SNAKE_CASE
    const MAX_PACKET_SIZE: usize = 65535;
    
    // ...
}

// エラーハンドリング: Result型を使用
pub fn risky_operation() -> Result<(), anyhow::Error> {
    // ?演算子でエラーを伝播
    let data = read_data()?;
    Ok(())
}
```

### TypeScript/Svelte

```typescript
// インターフェース名: PascalCase
interface MarketItem {
  // プロパティ名: camelCase
  itemId: string;
  itemName: string;
}

// 関数名: camelCase
function parseMarketData(data: any): MarketItem[] {
  // 定数: camelCase
  const maxItems = 100;
  
  // ...
}
```

### コメント

```rust
/// 関数の説明（ドキュメントコメント）
///
/// # Arguments
/// * `data` - パケットデータ
///
/// # Returns
/// パースされたMarketPacket、または失敗時はエラー
pub fn parse_packet(data: &[u8]) -> Result<MarketPacket> {
    // 実装の詳細（通常のコメント）
    let packet_type = identify_type(data);
    // ...
}
```

## ビルドとリリース

### デバッグビルド

```bash
npm run tauri:dev
```

### リリースビルド

```bash
# 最適化されたバイナリを生成
npm run tauri:build
```

ビルド成果物は `src-tauri/target/release/` に生成されます。

### インストーラーの作成

```bash
# Windowsインストーラー (.msi)
npm run tauri:build

# 生成されたインストーラーは以下に配置されます:
# src-tauri/target/release/bundle/msi/
```

## パフォーマンス最適化

### フロントエンド

1. **コンポーネントの遅延読み込み**
   ```svelte
   <script>
     import { onMount } from 'svelte';
     let HeavyComponent;
     
     onMount(async () => {
       HeavyComponent = (await import('./HeavyComponent.svelte')).default;
     });
   </script>
   ```

2. **不要な再レンダリングを避ける**
   ```svelte
   <script>
     let data = $state([]);
     // $stateを使用して細かい制御
   </script>
   ```

### バックエンド

1. **非同期処理の活用**
   ```rust
   // 並行処理
   use tokio::task::JoinSet;
   
   let mut set = JoinSet::new();
   for item in items {
       set.spawn(async move {
           process_item(item).await
       });
   }
   ```

2. **データベースクエリの最適化**
   ```rust
   // インデックスを活用
   // バッチ処理を使用
   // 不要なデータを取得しない
   ```

## トラブルシューティング

### ビルドエラー

**問題**: `cargo build` が失敗する

**解決策**:
```bash
# キャッシュをクリア
cargo clean
cargo build

# 依存関係を更新
cargo update
```

**問題**: `npm install` が失敗する

**解決策**:
```bash
# node_modulesを削除して再インストール
rm -rf node_modules
npm install

# または
npm ci
```

### ランタイムエラー

**問題**: WinDivertが起動しない

**解決策**:
1. 管理者権限で実行
2. アンチウイルスの除外設定に追加
3. VPNを無効化

**問題**: データベースが開けない

**解決策**:
```rust
// ログでパスを確認
info!("データベースパス: {:?}", db_path);

// ディレクトリの存在を確認
std::fs::create_dir_all(&parent_dir)?;
```

## CI/CD

### GitHub Actions (将来実装予定)

```yaml
# .github/workflows/build.yml
name: Build

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - uses: actions-rs/toolchain@v1
      - run: npm install
      - run: npm run tauri:build
      - uses: actions/upload-artifact@v3
        with:
          name: installer
          path: src-tauri/target/release/bundle/
```

## コントリビューション

1. Issueで議論してから実装を開始
2. フィーチャーブランチで開発
3. コミットメッセージは明確に
4. プルリクエストを作成

## 参考資料

- [Tauri Documentation](https://tauri.app/)
- [Svelte Documentation](https://svelte.dev/)
- [Rust Book](https://doc.rust-lang.org/book/)
- [WinDivert Documentation](https://www.reqrypt.org/windivert-doc.html)
- [BPSR Logs](https://github.com/winjwinj/bpsr-logs)
