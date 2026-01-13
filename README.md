# StarResonance Japan Market Analyzer

Blue Protocol: Star Resonance（日本版）のゲーム内取引所価格を取得・分析するツール

## 概要

このツールは、WinDivertを使用してゲームパケットを傍受し、取引所のアイテム価格データを収集します。
収集したデータを基に価格推移の分析や、将来的には損益計算機能を提供する予定です。

## 特徴

- 🚀 **リアルタイム価格取得**: WinDivertによるパケット傍受でゲーム内取引所価格を取得
- 📊 **価格推移の可視化**: アイテムごとの価格変動をグラフで表示
- 💰 **市場分析**: 取引傾向や価格統計の分析
- 🌐 **将来機能**: Web APIを通じた損益計算サイトの構築予定

## 技術スタック

- **フレームワーク**: Tauri 2.0
- **フロントエンド**: Svelte 5 / SvelteKit v2
- **バックエンド**: Rust
- **パケット傍受**: WinDivert
- **データベース**: SQLite (ローカル) / PostgreSQL (将来のWeb API用)

## インスピレーション

このプロジェクトは [BPSR Logs](https://github.com/winjwinj/bpsr-logs) にインスパイアされ、
同様のパケット解析手法を使用しています。

## 免責事項

- このツールの使用は自己責任で行ってください
- ゲームの利用規約を必ず確認してください
- 運営の方針変更により使用できなくなる可能性があります

## ライセンス

GNU Affero General Public License v3.0 (AGPL-3.0)

このプロジェクトはAGPL-3.0の下で公開されています。詳細は [LICENSE](LICENSE) を参照してください。

### サードパーティライセンス

- **WinDivert**: LGPL v3（動的リンクで使用）
- 詳細: [LICENSE_NOTES.md](LICENSE_NOTES.md) および [src-tauri/THIRD_PARTY_LICENSES.md](src-tauri/THIRD_PARTY_LICENSES.md)

### ライセンスの選択理由

- オープンソースコミュニティへの貢献
- 改変版のソース公開義務
- 将来のWeb API提供に最適
- WinDivert (LGPL) との互換性

## 開発状況

🚧 **現在開発中** 🚧

### 完了
- [ ] プロジェクト基本構造
- [ ] WinDivertパケット傍受機能
- [ ] パケットパーサー実装
- [ ] 取引所データ抽出
- [ ] データベース設計
- [ ] 基本UI実装

### 予定
- [ ] 価格推移グラフ
- [ ] 市場分析機能
- [ ] Web API開発
- [ ] 損益計算サイト

## 📖 ドキュメント

### ユーザー向け
- **[クイックスタートガイド](QUICKSTART.md)** - 最速で始める方法
- **[インストールガイド](INSTALLATION.md)** - 詳細なインストール手順とトラブルシューティング

### 開発者向け
- **[開発ガイド](docs/DEVELOPMENT.md)** - 開発環境のセットアップと開発ワークフロー
- **[パケット解析ガイド](docs/PACKET_ANALYSIS.md)** - WinDivertとパケット解析の詳細
- **[API設計書](docs/API_DESIGN.md)** - 将来のWeb APIの設計
- **[ロードマップ](docs/ROADMAP.md)** - プロジェクトの今後の予定
- **[コントリビューションガイド](CONTRIBUTING.md)** - プロジェクトへの貢献方法

## 🚀 クイックスタート

### ユーザー向け

```bash
# 1. 最新版をダウンロード
# https://github.com/yourusername/StarResonance_Japan_Market_Analyzer/releases

# 2. インストーラーを管理者権限で実行
# 右クリック → 管理者として実行

# 3. アプリを起動して「監視開始」
```

詳細: [QUICKSTART.md](QUICKSTART.md)

### 開発者向け（Windows）⭐ おすすめ

**バッチファイルで簡単起動！**

```batch
# 1. リポジトリをクローン
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer

# 2. ダブルクリックで起動（自動的に管理者権限に昇格）
start-dev-auto-admin.bat
```

その他の便利なバッチファイル:
- `build.bat` - リリースビルド
- `run.bat` - ビルド済みアプリを実行
- `clean.bat` - キャッシュクリア

詳細: [BATCH_SCRIPTS.md](BATCH_SCRIPTS.md)

### 開発者向け（手動）

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer

# 依存関係のインストール
npm install

# 開発モードで起動（管理者権限が必要）
npm run tauri dev

# ビルド
npm run tauri build
```

詳細: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## WinDivertについて

このツールはWinDivert64.sysドライバーを使用します。
一部のアンチウイルスソフトが誤検知する場合がありますが、コードはオープンソースで公開されています。

### 誤検知への対処

1. Windows Defenderの除外設定に追加
2. プロジェクトフォルダ全体を信頼済みとして設定

## コントリビューション

プロジェクトへの貢献を歓迎します！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## サポート

問題が発生した場合は、Issuesセクションで報告してください。

## 将来の展望

### Phase 1: デスクトップアプリ（現在）
- ローカルでの価格データ収集
- 基本的な分析機能

### Phase 2: データ共有機能
- ユーザー間でのデータ共有
- コミュニティ価格データベース

### Phase 3: Web サービス
- オンライン損益計算サイト
- API提供
- 高度な市場分析機能

## FAQ

### Q: これは安全ですか？
A: コードはオープンソースで公開されており、誰でも確認できます。WinDivertは正規のパケットキャプチャツールです。

### Q: BANされませんか？
A: 同様の手法を使うBPSR Logsは運営に認知されていますが、このツール独自の保証はありません。使用は自己責任でお願いします。

### Q: パケットが検出されません
A: VPN（特にNordVPN）やExitLagなどのツールと競合する可能性があります。設定を確認してください。

## 連絡先

プロジェクトに関する質問や提案がある場合は、Issuesまでお願いします。

---

**注意**: このツールはファンメイドであり、ゲーム運営とは一切関係ありません。
