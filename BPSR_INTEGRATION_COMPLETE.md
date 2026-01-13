# BPSR Logs 統合完了 ✅

## 🎉 実装完了

BPSR Logsの実装を参考に、パケットキャプチャ機能を大幅に改善しました！

### 統合した機能

#### 1. **WinDivertフィルタ** ✅
```rust
"!loopback && ip && tcp"
```
- BPSR Logsと同じフィルタを使用
- ループバック以外の全TCP/IPパケットをキャプチャ
- ゲームサーバーはパケット内容で動的に識別

#### 2. **ゲームサーバー自動識別** ✅
```rust
const GAME_SERVER_SIGNATURE: [u8; 6] = [0x00, 0x63, 0x33, 0x53, 0x42, 0x00];
```

2つの方法でゲームサーバーを識別:
- **シグネチャ検出**: 特定のバイトパターンでゲームサーバーを識別
- **ログインパケット検出**: ログイン時のパケットで識別

#### 3. **TCP再組立機能** ✅
`src-tauri/src/tcp_reassembler.rs`

- TCPパケットの順序を管理
- 分割されたパケットを再構築
- シーケンス番号でパケットを追跡

#### 4. **ゲームパケット解析** ✅
`src-tauri/src/game_packet.rs`

- パケット構造の定義
- Notify/FrameDownパケットのサポート
- zstd圧縮のサポート

### 新しいファイル

1. **`src-tauri/src/tcp_reassembler.rs`**
   - TCP再組立ロジック
   - シーケンス番号管理
   - パケット抽出

2. **`src-tauri/src/game_packet.rs`**
   - ゲームパケット構造
   - パケット解析
   - 圧縮解除

### 更新したファイル

1. **`src-tauri/src/packet_capture.rs`**
   - BPSR Logsの実装を統合
   - ゲームサーバー自動識別
   - TCP再組立の統合
   - 10MBバッファ（BPSR Logsと同じ）

2. **`src-tauri/Cargo.toml`**
   - `zstd` クレートを追加

3. **`src-tauri/src/main.rs`**
   - 新モジュールの追加

## 🚀 動作確認

### 期待される動作

1. **アプリ起動**
   ```bash
   start-dev-auto-admin.bat
   ```

2. **監視開始**
   - 「監視開始」ボタンをクリック

3. **ゲーム起動**
   - Blue Protocol: Star Resonance を起動
   - ログインしてキャラクター選択

4. **ゲームサーバー検出**
   - ログに以下のような出力が表示されるはず:
   ```
   [INFO] Game server detected (by signature): 123.45.67.89:12345 -> 192.168.1.100:54321
   ```
   または
   ```
   [INFO] Game server detected (by login): 123.45.67.89:12345 -> 192.168.1.100:54321
   ```

5. **パケット処理**
   - ゲームサーバーが検出されたら、パケットの処理が開始
   ```
   [DEBUG] Game packet: type=0000, compressed=false, size=256
   ```

### ログの確認場所

- **開発モード**: コンソール出力
- **リリースモード**: 
  ```
  %LOCALAPPDATA%\StarResonance_Market_Analyzer\logs\
  ```

## 📊 現在の状態

### ✅ 実装済み
- [x] WinDivert動的ロード
- [x] WinDivertフィルタ（BPSR Logs準拠）
- [x] ゲームサーバー自動識別
- [x] TCP再組立
- [x] ゲームパケット基本解析
- [x] 圧縮サポート（zstd）

### ⏳ 次のステップ
- [ ] 取引所パケットの識別
- [ ] 市場データの抽出
- [ ] データベースへの保存
- [ ] 実ゲームでのテスト

## 🔍 BPSR Logsとの違い

### 同じ部分
- WinDivertフィルタ
- ゲームサーバー識別ロジック
- TCP再組立の基本構造
- パケット構造の理解

### 異なる部分
- **目的**: BPSR Logs = DPS計測、当プロジェクト = 取引所データ
- **パケット処理**: DPSパケット vs 市場データパケット
- **UI**: BPSR Logs = オーバーレイ、当プロジェクト = 市場分析

## 🎯 次の実装タスク

### 1. 取引所パケットの識別 🔴
- 取引所を開いたときのパケットを特定
- method_id を確認

### 2. 市場データの抽出 🔴
- アイテムID、名前、価格、数量の抽出
- バイナリフォーマットの解析

### 3. データベース保存 🟡
- 抽出したデータをSQLiteに保存
- 重複チェック

### 4. 実ゲームテスト 🟢
- 実際のゲームで動作確認
- パケットログの収集

## 💡 デバッグ方法

### パケットダンプを有効化
`src-tauri/src/packet_capture.rs` の `process_game_packet` に追加:

```rust
fn process_game_packet(data: &[u8], _db: &Arc<Mutex<Database>>) -> Result<bool> {
    let packet = GamePacket::parse(data)?;
    
    // ダンプを有効化
    if packet.payload.len() > 0 {
        info!("Packet dump (first 64 bytes):");
        for (i, chunk) in packet.payload.chunks(16).take(4).enumerate() {
            let hex: String = chunk.iter().map(|b| format!("{:02X} ", b)).collect();
            info!("  {:04X}: {}", i * 16, hex);
        }
    }
    
    // ...
}
```

## 🙏 クレジット

Based on [BPSR Logs](https://github.com/winjwinj/bpsr-logs) by winj
- Licensed under GPL-3.0
- パケットキャプチャの実装を参考にしました
- 特にゲームサーバー識別とTCP再組立のロジックを継承

## 📝 ライセンス

本プロジェクトは AGPL-3.0 ライセンスです。
BPSR Logs (GPL-3.0) のコードを統合しているため、GPL互換性を維持しています。

---

## 🚀 今すぐテスト！

```bash
# 管理者権限で起動
start-dev-auto-admin.bat
```

ゲームサーバーが検出されるか確認してください！ 🎮
