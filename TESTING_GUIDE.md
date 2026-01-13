# テストガイド

## 🎮 実ゲームでのテスト手順

### 準備

1. **アプリをビルド**
   ```bash
   start-dev-auto-admin.bat
   ```

2. **Blue Protocol: Star Resonance を起動準備**
   - ゲームクライアントを起動できる状態にする
   - ログイン情報を準備

### テスト手順

#### Phase 1: ゲームサーバー検出テスト 🔴

1. **アプリを起動**
   - `start-dev-auto-admin.bat` を実行
   - 管理者権限が付与されていることを確認

2. **監視開始**
   - 「監視開始」ボタンをクリック
   - ステータスが「監視中」になることを確認

3. **ゲームを起動**
   - Blue Protocol: Star Resonance を起動
   - ログイン画面まで進む

4. **ログを確認**
   - コンソールに以下のようなログが出力されるか確認:
   ```
   [INFO] WinDivert handle opened
   [INFO] Packet capture started. Waiting for game server...
   ```

5. **ログイン**
   - ゲームにログイン
   - キャラクター選択画面まで進む

6. **ゲームサーバー検出を確認**
   - 以下のいずれかのログが出力されるはず:
   ```
   [INFO] Game server detected (by signature): <IP>:<Port> -> <IP>:<Port>
   ```
   または
   ```
   [INFO] Game server detected (by login): <IP>:<Port> -> <IP>:<Port>
   ```

#### Phase 2: パケット処理テスト 🟡

1. **キャラクターでログイン**
   - ゲーム内に入る

2. **ログを確認**
   - パケットが処理されているか確認:
   ```
   [DEBUG] Game packet: type=XXXX, compressed=true/false, size=XXX
   ```

3. **パケットカウントを確認**
   - 1000パケットごとにログが出力されるはず:
   ```
   [DEBUG] Packets received: 1000, Game packets: XX
   ```

#### Phase 3: 取引所パケット識別テスト 🟢

1. **取引所を開く**
   - ゲーム内で取引所NPCに話しかける
   - 取引所UIを開く

2. **ログを収集**
   - 取引所を開く前後のパケットログを確認
   - パケットタイプやサイズの変化を観察

3. **アイテムを検索**
   - 取引所で何かアイテムを検索
   - パケットの変化を観察

4. **取引所を閉じる**
   - 再度開いて、同じパケットパターンが出現するか確認

### ログの確認方法

#### コンソール出力（開発モード）
- PowerShellウィンドウに直接出力される
- リアルタイムで確認可能

#### ログファイル（リリースモード）
```
%LOCALAPPDATA%\StarResonance_Market_Analyzer\logs\
```

### 期待される結果

#### Phase 1 成功時
```
[INFO] StarResonance Market Analyzer を起動しています...
[INFO] データベースが正常に初期化されました
[INFO] Initializing WinDivert...
[INFO] Filter: !loopback && ip && tcp
[INFO] WinDivert DLL loaded from: ...
[INFO] WinDivert opened successfully with filter: !loopback && ip && tcp
[INFO] Packet capture started. Waiting for game server...
[DEBUG] Packets received: 1000, Game packets: 0
[INFO] Game server detected (by login): 123.45.67.89:12345 -> 192.168.1.100:54321
[DEBUG] Packets received: 2000, Game packets: 15
[DEBUG] Game packet: type=0000, compressed=false, size=256
```

#### Phase 2 成功時
```
[DEBUG] Game packets: 100 (processing...)
```

#### Phase 3 成功時
（取引所パケットの特定）
```
[DEBUG] Potential market packet: type=XXXX, size=YYYY
```

## 🐛 トラブルシューティング

### ゲームサーバーが検出されない

**原因1: VPNやネットワークツールの干渉**
- NordVPNなど、WinDivertを使用する他のツールを終了
- 解決策: VPNを完全に終了してPCを再起動

**原因2: 管理者権限不足**
- 確認: コンソールに「管理者権限が必要です」と表示されていないか
- 解決策: `start-dev-auto-admin.bat` を使用

**原因3: WinDivertファイルの欠損**
- 確認: `src-tauri/WinDivert64.dll` と `WinDivert64.sys` が存在するか
- 解決策: リポジトリを再クローンまたはファイルを復元

### パケットが処理されない

**原因1: ゲームサーバー未検出**
- Phase 1のログを確認
- ゲームに再ログイン

**原因2: パケット解析エラー**
- ログに `Malformed packet` エラーがないか確認
- パケットダンプを有効化してデータを確認

### アプリがクラッシュする

**原因1: WinDivertエラー**
- ログに WinDivert 関連のエラーがないか確認
- PCを再起動してWinDivertドライバをリセット

**原因2: メモリ不足**
- 大量のパケットでメモリ消費が増加
- アプリを再起動

## 📊 データ収集

### パケットダンプの取得

取引所パケットを特定するため、パケットダンプを収集:

1. **ダンプ機能を有効化**
   `src-tauri/src/packet_capture.rs` の `process_game_packet` に追加:

```rust
fn process_game_packet(data: &[u8], _db: &Arc<Mutex<Database>>) -> Result<bool> {
    let packet = GamePacket::parse(data)?;
    
    // 全パケットをダンプ
    info!("=== Packet Dump ===");
    info!("Type: {:04X}, Compressed: {}, Size: {}", 
        packet.packet_type, packet.is_compressed, packet.size);
    
    if packet.payload.len() > 0 {
        let preview_len = packet.payload.len().min(256);
        for (i, chunk) in packet.payload[..preview_len].chunks(16).enumerate() {
            let hex: String = chunk.iter().map(|b| format!("{:02X} ", b)).collect();
            let ascii: String = chunk.iter().map(|b| {
                if *b >= 32 && *b <= 126 { *b as char } else { '.' }
            }).collect();
            info!("{:04X}: {} | {}", i * 16, hex, ascii);
        }
        if packet.payload.len() > preview_len {
            info!("... ({} more bytes)", packet.payload.len() - preview_len);
        }
    }
    info!("==================");
    
    Ok(false)
}
```

2. **取引所で以下の操作を実行**
   - 取引所を開く
   - アイテムを検索
   - ページをめくる
   - アイテム詳細を見る
   - 取引所を閉じる

3. **ログを保存**
   - コンソール出力をファイルにリダイレクト
   - または、ログファイルをコピー

### 共有すべき情報

取引所パケットを特定したら、以下を共有:

1. **パケットタイプ**: `type=XXXX`
2. **パケットサイズ**: `size=YYYY`
3. **パケットダンプ**: 16進数とASCII
4. **操作内容**: どの操作でこのパケットが出現したか

## 🎯 次のステップ

Phase 3で取引所パケットを特定できたら:
1. パケットタイプを記録
2. データ構造を解析
3. パーサーを実装
4. データベースに保存

頑張ってください！🚀
