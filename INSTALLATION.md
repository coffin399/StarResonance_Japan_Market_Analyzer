# インストールガイド

## システム要件

- **OS**: Windows 7以上（64-bit推奨）
- **メモリ**: 4GB以上推奨
- **ストレージ**: 500MB以上の空き容量
- **権限**: 管理者権限が必要
- **その他**: Microsoft Edge WebView2 Runtime

## インストール手順

### 方法1: インストーラーを使用（推奨）

1. **ダウンロード**
   - [Releases](https://github.com/yourusername/StarResonance_Japan_Market_Analyzer/releases/latest) から最新版をダウンロード
   - `StarResonance-Market-Analyzer_[version]_x64.msi` を選択

2. **インストール**
   - ダウンロードしたMSIファイルを右クリック
   - 「管理者として実行」を選択
   - インストーラーの指示に従う

3. **初回起動**
   - スタートメニューから「StarResonance Market Analyzer」を起動
   - Windows Defenderの警告が出る場合は「詳細情報」→「実行」をクリック

### 方法2: ソースからビルド

開発者向け。詳細は [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) を参照してください。

```bash
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer
npm install
npm run tauri:build
```

## 依存関係

### Microsoft Edge WebView2 Runtime

Tauriアプリケーションの実行に必要です。

**インストール済みか確認:**
```
C:\Program Files (x86)\Microsoft\EdgeWebView\Application
```
上記のフォルダが存在すればインストール済みです。

**インストールしていない場合:**
1. [Microsoft Edge WebView2](https://go.microsoft.com/fwlink/p/?LinkId=2124703) からダウンロード
2. インストーラーを実行

## トラブルシューティング

### インストーラーが起動しない

**原因**: 管理者権限がない

**解決策**:
- MSIファイルを右クリック → 「管理者として実行」

### "WinDivert64.sys が見つかりません"

**原因**: WinDivertドライバーがブロックされている

**解決策**:
1. Windows Defenderの除外設定に追加
   - Windows セキュリティ を開く
   - ウイルスと脅威の防止 → 設定の管理
   - 除外 → 除外を追加
   - フォルダーを選択し、インストールフォルダを追加

2. アプリを再インストール

### アンチウイルスが検知する

**原因**: WinDivertが誤検知される

**解決策**:
- コードはオープンソースで確認可能です
- アンチウイルスの除外設定に追加
- 詳細は [README.md](README.md#does-it-mine-bitcoin) を参照

### VPN使用時に動作しない

**原因**: VPN（特にNordVPN）がWinDivertと競合

**解決策**:
- VPNを完全に終了
- コンピュータを再起動
- アプリを起動してからVPNを起動（非推奨）

### ExitLag使用時に動作しない

**原因**: ExitLagの設定

**解決策**:
ExitLagの設定を変更:
1. ExitLagを開く
2. 設定 → 詳細設定
3. **Packet redirection method** を **Legacy - NDIS** に変更
4. ExitLagを再起動

### "管理者権限が必要です"というエラー

**原因**: アプリが管理者権限で起動されていない

**解決策**:
- アプリを右クリック → 「管理者として実行」
- 常に管理者権限で起動する設定:
  1. アプリを右クリック → プロパティ
  2. 互換性タブ
  3. 「管理者としてこのプログラムを実行する」にチェック

## アンインストール

### Windows 設定から

1. 設定 → アプリ → インストールされているアプリ
2. "StarResonance Market Analyzer" を検索
3. ... → アンインストール

### コマンドラインから

```powershell
# 管理者権限のPowerShellで実行
wmic product where "name='StarResonance Market Analyzer'" call uninstall
```

### 完全削除

アンインストール後、以下のフォルダも手動で削除できます:

```
%LOCALAPPDATA%\StarResonance_Market_Analyzer\
```

データベースファイルも削除されます。

## データのバックアップ

データベースをバックアップしたい場合:

```
%LOCALAPPDATA%\StarResonance_Market_Analyzer\market_data.db
```

上記のファイルをコピーして保存してください。

## アップデート

### 自動更新（将来実装予定）

アプリ起動時に自動的に更新をチェックします。

### 手動更新

1. 現在のバージョンをアンインストール
2. 新しいバージョンをダウンロード
3. インストール

データベースは保持されます。

## サポート

問題が解決しない場合:

1. [GitHub Issues](https://github.com/yourusername/StarResonance_Japan_Market_Analyzer/issues) で検索
2. 新しいIssueを作成（以下の情報を含める）:
   - Windowsバージョン
   - アプリバージョン
   - エラーメッセージ
   - 実行した手順
   - スクリーンショット（可能であれば）

## セキュリティ

このアプリケーションは:
- ✅ オープンソース
- ✅ ローカルでのみデータを保存
- ✅ 外部サーバーへの通信なし（現バージョン）
- ✅ ゲームデータの改ざんなし

安心してご使用ください。
