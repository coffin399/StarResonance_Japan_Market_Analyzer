# クイックスタートガイド

StarResonance Market Analyzerを素早く始めるためのガイドです。

## 📦 インストール

### 方法1: プリビルド版（一般ユーザー向け）

1. [Releases](https://github.com/yourusername/StarResonance_Japan_Market_Analyzer/releases/latest) ページへ
2. 最新版の `.msi` ファイルをダウンロード
3. **右クリック** → **管理者として実行**
4. インストーラーの指示に従う

詳細: [INSTALLATION.md](INSTALLATION.md)

### 方法2: ソースからビルド（開発者向け）

```bash
# 前提条件: Node.js, Rust, Tauri CLIがインストール済み

# リポジトリのクローン
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer

# 依存関係のインストール
npm install

# 開発モードで起動
npm run tauri:dev
```

詳細: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

## 🚀 初回起動

### 1. 管理者権限で実行

**重要**: このアプリはWinDivertを使用するため、**管理者権限が必須**です。

```
右クリック → 管理者として実行
```

または、常に管理者権限で起動する設定:

```
右クリック → プロパティ → 互換性 → 「管理者としてこのプログラムを実行する」
```

### 2. Windows Defenderの警告

初回起動時にWindows Defenderが警告を出す場合:

```
「詳細情報」をクリック → 「実行」をクリック
```

### 3. 除外設定の追加（推奨）

WinDivertが誤検知される場合:

1. **Windows セキュリティ** を開く
2. **ウイルスと脅威の防止** → **設定の管理**
3. **除外** → **除外を追加**
4. インストールフォルダ全体を追加

例: `C:\Program Files\StarResonance Market Analyzer\`

## 📊 使い方

### 基本的な流れ

```
1. アプリを起動
   ↓
2. 「監視開始」ボタンをクリック
   ↓
3. Blue Protocol: Star Resonance を起動
   ↓
4. ゲーム内で取引所を開く
   ↓
5. 価格データが自動的に記録される！
```

### 画面の説明

#### メインダッシュボード

```
┌──────────────────────────────────────────────┐
│  ⭐ StarResonance Market Analyzer           │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ 🟢 取引所データを監視中...             │ │
│  │                    [⏹️ 監視停止]        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  📈 取引所データ                             │
│  ┌────────────────────────────────────────┐ │
│  │ アイテム名  │ 現在価格 │ 出品数 │ 更新 │ │
│  │ レア武器    │ 150,000G │   5   │ 1分前│ │
│  │ ...        │ ...     │  ...  │ ...  │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

### 主な機能

#### 1. リアルタイム監視
- ゲーム内の取引所価格を自動取得
- バックグラウンドで動作

#### 2. 価格履歴
- アイテムごとの価格推移を記録
- グラフで可視化（今後実装予定）

#### 3. データエクスポート
- CSV形式でのエクスポート（今後実装予定）
- 他のツールとの連携

## ⚠️ トラブルシューティング

### パケットが検出されない

**確認事項**:
- ✅ 管理者権限で実行しているか？
- ✅ VPNを使用していないか？
- ✅ ゲームが起動しているか？
- ✅ 取引所を開いているか？

**解決策**:
```powershell
# 1. アプリを完全に終了
# 2. VPNを無効化（NordVPNの場合は完全アンインストール）
# 3. PCを再起動
# 4. アプリを管理者権限で起動
# 5. ゲームを起動して取引所を開く
```

### VPN使用時の注意

**NordVPN**: WinDivertと競合するため、使用できません。

**ExitLag**: 設定変更が必要
```
ExitLag設定 → 詳細設定
Packet redirection method → Legacy - NDIS
```

### エラーメッセージ

| エラー | 原因 | 解決策 |
|--------|------|--------|
| "WinDivert64.sys が見つかりません" | ドライバーがブロックされている | 除外設定に追加、再インストール |
| "管理者権限が必要です" | 通常権限で起動している | 管理者として実行 |
| "パケットキャプチャの開始に失敗" | VPNまたは他のソフトが干渉 | VPNを無効化、再起動 |

## 💡 Tips & Tricks

### 1. 自動起動
Windowsのスタートアップに登録:
```
Win + R → shell:startup → ショートカットを配置
```

### 2. データのバックアップ
データベースファイルの場所:
```
%LOCALAPPDATA%\StarResonance_Market_Analyzer\market_data.db
```

定期的にバックアップを取ることをお勧めします。

### 3. 複数キャラクター
- 各キャラクターのデータは自動的に統合されます
- サーバーごとに分けることも可能（今後実装予定）

## 🎯 次のステップ

### ユーザー向け
1. ✅ 基本的な使い方をマスター
2. 📊 価格データを収集
3. 💰 市場トレンドを分析
4. 🌐 Web版の損益計算サイトを待つ（開発中）

### 開発者向け
1. ✅ 開発環境のセットアップ ([docs/DEVELOPMENT.md](docs/DEVELOPMENT.md))
2. 🔍 パケット解析の理解 ([docs/PACKET_ANALYSIS.md](docs/PACKET_ANALYSIS.md))
3. 🚀 機能の実装 ([docs/ROADMAP.md](docs/ROADMAP.md))
4. 🤝 プルリクエストの作成 ([CONTRIBUTING.md](CONTRIBUTING.md))

## 📚 詳細なドキュメント

- **インストール**: [INSTALLATION.md](INSTALLATION.md)
- **開発ガイド**: [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **パケット解析**: [docs/PACKET_ANALYSIS.md](docs/PACKET_ANALYSIS.md)
- **API設計**: [docs/API_DESIGN.md](docs/API_DESIGN.md)
- **ロードマップ**: [docs/ROADMAP.md](docs/ROADMAP.md)

## 🤝 サポート & コミュニティ

- **バグ報告**: [GitHub Issues](https://github.com/yourusername/StarResonance_Japan_Market_Analyzer/issues)
- **質問**: [GitHub Discussions](https://github.com/yourusername/StarResonance_Japan_Market_Analyzer/discussions)
- **Discord**: （準備中）

## ❓ FAQ

### Q: これは安全ですか？
A: はい。コードはすべてオープンソースで公開されており、誰でも確認できます。WinDivertは正規のパケットキャプチャツールです。

### Q: BANされませんか？
A: BPSR Logsが運営に認知されており、同様の手法を使用しています。ただし、使用は自己責任でお願いします。

### Q: なぜ管理者権限が必要ですか？
A: WinDivertドライバーをロードするためにWindowsの管理者権限が必要です。

### Q: オフラインで使えますか？
A: 現バージョンはローカルで動作しますが、ゲームサーバーに接続している必要があります。

### Q: 他のプレイヤーのデータも見えますか？
A: いいえ。あなたのクライアントが受信したパケットのみを解析します。

### Q: ゲームに影響はありますか？
A: いいえ。パケットを傍受して記録するだけで、ゲームの動作には影響しません。

## 🎉 はじめましょう！

準備ができたら、今すぐアプリを起動して取引所データの収集を始めましょう！

```bash
# インストール済みの場合
スタートメニュー → StarResonance Market Analyzer

# ソースから実行する場合
npm run tauri:dev
```

何か問題があれば、遠慮なく [Issue を作成](https://github.com/yourusername/StarResonance_Japan_Market_Analyzer/issues/new) してください！

---

**Happy Trading! 📈✨**
