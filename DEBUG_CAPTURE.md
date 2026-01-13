# パケットキャプチャデバッグガイド

## 現在の状況

✅ **パケット受信**: OK (1000パケット受信確認済み)
❌ **ゲームサーバー検出**: NG (0個)

## 次のステップ

### 1. サンプルパケットの確認

500パケットごとにサンプルパケットをログ出力するようにしました。

**確認すべき情報**:
```
[DEBUG] Sample packet: IP:Port -> IP:Port, payload_len=XXX
[DEBUG]   Payload preview: 00 01 02 03 ...
```

### 2. ゲーム起動シーケンス

#### 期待される動作:
1. **アプリ起動** → 監視開始
2. **ゲーム起動前**: 一般的なTCPパケットのみ
3. **ゲーム起動**: 
   - ゲームサーバーへの接続開始
   - ログインパケット（98バイト）が送信される
4. **ログイン成功**:
   - ゲームサーバーから特定のシグネチャを含むパケットが返ってくる
5. **サーバー検出**: `🎮 Game server detected` ログが出力される

### 3. トラブルシューティング

#### シナリオA: ゲームを起動していない
**症状**: パケットは受信するが、ゲームサーバーが検出されない
**対策**: ゲームを起動してログインする

#### シナリオB: ゲームは起動しているが検出されない
**症状**: ゲーム起動後もゲームサーバーが検出されない
**原因**: 
- パケット構造が想定と異なる
- 暗号化されている
- 別のプロトコルを使用

**デバッグ方法**:
1. サンプルパケットログを確認
2. ゲームサーバーのIPアドレスを特定
3. そのIPへのパケットをダンプ

#### シナリオC: VPN/プロキシ経由
**症状**: パケットが見えない、または異なる構造
**対策**: VPNを無効化してテスト

## デバッグ用の追加コード

### 特定IPのパケットを詳細ダンプ

`src-tauri/src/packet_capture.rs` の該当箇所に追加:

\`\`\`rust
// ゲームサーバーのIPが分かっている場合
const KNOWN_GAME_SERVER_IP: &str = "123.45.67.89"; // 実際のIPに置き換え

if source_ip.to_string() == KNOWN_GAME_SERVER_IP || dest_ip.to_string() == KNOWN_GAME_SERVER_IP {
    info!("=== Game server packet ===");
    info!("{}:{} -> {}:{}", source_ip, source_port, dest_ip, dest_port);
    info!("Payload length: {}", tcp_payload.len());
    
    if tcp_payload.len() > 0 {
        let preview_len = tcp_payload.len().min(128);
        for (i, chunk) in tcp_payload[..preview_len].chunks(16).enumerate() {
            let hex: String = chunk.iter().map(|b| format!("{:02X} ", b)).collect();
            info!("{:04X}: {}", i * 16, hex);
        }
    }
}
\`\`\`

## ゲームサーバーIPの特定方法

### 方法1: netstatコマンド

1. ゲームを起動
2. PowerShellで実行:
   \`\`\`powershell
   netstat -ano | findstr "ESTABLISHED" | findstr "<ゲームプロセス名>"
   \`\`\`

3. ゲームプロセスのPIDを取得:
   \`\`\`powershell
   tasklist | findstr "Blue"
   \`\`\`

4. そのPIDの接続を確認:
   \`\`\`powershell
   netstat -ano | findstr "<PID>"
   \`\`\`

### 方法2: リソースモニター

1. `resmon` を起動
2. 「ネットワーク」タブ
3. ゲームプロセスを探す
4. 接続先アドレスを確認

### 方法3: Wireshark

1. Wiresharkをインストール
2. キャプチャ開始
3. ゲームを起動
4. フィルタ: `tcp && !ip.addr == 127.0.0.1`
5. ゲームサーバーと思われる接続を探す

## 次のアクション

1. **ゲームを起動してログを確認**
   - サンプルパケットが表示されるか
   - ゲーム起動前後でパケットが変化するか

2. **ゲームサーバーIPを特定**
   - netstatまたはリソースモニターで確認

3. **特定IPのパケットをダンプ**
   - デバッグコードを追加して詳細を確認

4. **パケット構造を分析**
   - ダンプしたデータから特徴を探す
   - BPSR Logsのシグネチャと比較
