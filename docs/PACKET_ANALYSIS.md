# パケット解析ガイド

## 概要

このドキュメントでは、Blue Protocol: Star Resonanceのゲームパケットを解析する方法について説明します。

## 前提知識

### WinDivertとは

WinDivertは、Windowsネットワークスタック上でパケットをキャプチャ、変更、ドロップできるユーザーモードのライブラリです。

**特徴:**
- カーネルモードドライバーとユーザーモードDLLで構成
- 管理者権限が必要
- 柔軟なフィルタリング機能

### パケットキャプチャの流れ

```
1. WinDivertドライバーをロード
2. フィルタを設定（特定のIPアドレス/ポートのみ）
3. パケットを受信
4. パケットをパース
5. 取引所データを抽出
6. データベースに保存
7. パケットを再注入（ゲームに影響を与えないため）
```

## パケット構造の調査方法

### 1. Wiresharkでの基本調査

```bash
# Wiresharkフィルタ例
tcp.port == [ゲームポート]
ip.addr == [ゲームサーバーIP]
```

### 2. パケットの特徴を見つける

取引所を開いた時のパケットを特定するために:

1. ゲームを起動してログイン（パケットキャプチャ開始）
2. 取引所を開く
3. アイテムを検索/閲覧
4. 取引所を閉じる
5. パケットキャプチャ停止

**注目すべきポイント:**
- パケットサイズの変化
- 特定のバイトパターン
- TCPシーケンス番号
- タイミング

### 3. パケットヘッダーの解析

多くのゲームは以下のような構造を使用:

```
[マジックナンバー: 4バイト]
[パケットタイプ: 2バイト]
[ペイロード長: 4バイト]
[シーケンス番号: 4バイト]
[ペイロード: 可変長]
[チェックサム: 4バイト]
```

### 4. ペイロードの解析

#### 取引所アイテムリストの例

```
想定される構造:
[アイテム数: 2バイト] (例: 0x000A = 10アイテム)

各アイテム:
  [アイテムID: 8バイト]     (例: 0x0000000000001234)
  [価格: 8バイト]           (例: 0x000000000002BF20 = 180,000)
  [数量: 4バイト]           (例: 0x00000005 = 5個)
  [出品者名の長さ: 2バイト] (例: 0x0008 = 8文字)
  [出品者名: UTF-8可変長]   (例: "Player01")
  [アイテム名の長さ: 2バイト]
  [アイテム名: UTF-8可変長] (例: "レア武器")
```

## WinDivertの使用例

### フィルタの設定

```rust
use windivert::WinDivert;

// Blue Protocolのサーバーへの接続をフィルタ
let filter = "tcp and (remoteAddr == 123.45.67.89 or remoteAddr == 123.45.67.90)";

// WinDivertを初期化
let divert = WinDivert::new(filter, 0, 0, 0)?;
```

### パケットの受信

```rust
let mut buffer = vec![0u8; 65535];
let mut addr = WinDivertAddress::default();

loop {
    // パケットを受信
    let packet_len = divert.recv(&mut buffer, &mut addr)?;
    let packet = &buffer[..packet_len];

    // パケットを解析
    if is_market_packet(packet) {
        let market_data = parse_market_packet(packet)?;
        save_to_database(market_data)?;
    }

    // パケットを再注入（ゲームに届ける）
    divert.send(&buffer[..packet_len], &addr)?;
}
```

## パケット解析のベストプラクティス

### 1. バイトオーダーの確認

ゲームによってリトルエンディアンかビッグエンディアンか異なる:

```rust
// リトルエンディアン（一般的）
let price = u64::from_le_bytes([b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]]);

// ビッグエンディアン
let price = u64::from_be_bytes([b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]]);
```

### 2. 文字列エンコーディング

```rust
// UTF-8（推奨）
let item_name = String::from_utf8(bytes)?;

// UTF-16（一部のゲームで使用）
let item_name = String::from_utf16(&bytes)?;

// Shift-JIS（古い日本のゲーム）
// 外部クレート（encoding_rs）が必要
```

### 3. エラーハンドリング

```rust
fn parse_packet(data: &[u8]) -> Result<MarketPacket> {
    // 最小パケットサイズのチェック
    if data.len() < MIN_PACKET_SIZE {
        return Err(anyhow!("パケットが小さすぎます"));
    }

    // マジックナンバーの確認
    if !has_valid_magic_number(data) {
        return Err(anyhow!("無効なマジックナンバー"));
    }

    // ... パース処理
}
```

## デバッグ技法

### 1. パケットダンプ

```rust
fn dump_packet(data: &[u8]) {
    println!("パケット長: {} バイト", data.len());
    println!("先頭16バイト: {:02X?}", &data[..16.min(data.len())]);
    
    // ヘキサダンプ
    for (i, chunk) in data.chunks(16).enumerate() {
        print!("{:04X}: ", i * 16);
        for byte in chunk {
            print!("{:02X} ", byte);
        }
        println!();
    }
}
```

### 2. パケットログファイル

```rust
use std::fs::OpenOptions;
use std::io::Write;

fn log_packet_to_file(packet: &[u8]) -> Result<()> {
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open("packet_log.bin")?;
    
    // タイムスタンプ + パケット長 + パケットデータ
    let timestamp = Utc::now().timestamp();
    file.write_all(&timestamp.to_le_bytes())?;
    file.write_all(&(packet.len() as u32).to_le_bytes())?;
    file.write_all(packet)?;
    
    Ok(())
}
```

### 3. パターン認識

```rust
fn find_common_patterns(packets: &[Vec<u8>]) {
    // すべてのパケットで共通のバイトパターンを見つける
    for pos in 0..packets[0].len() {
        let first_byte = packets[0][pos];
        if packets.iter().all(|p| p.len() > pos && p[pos] == first_byte) {
            println!("位置 {} に共通バイト: 0x{:02X}", pos, first_byte);
        }
    }
}
```

## トラブルシューティング

### パケットが取得できない

**原因:**
1. VPNやプロキシが干渉している
2. フィルタが正しくない
3. 管理者権限がない

**解決策:**
```powershell
# 管理者権限で実行
Right-click → Run as Administrator

# VPNを無効化
# ExitLagの場合は設定を変更: Packet redirection method > Legacy - NDIS
```

### パケットが解析できない

**原因:**
1. 暗号化されている
2. 圧縮されている
3. パケット構造が想定と異なる

**解決策:**
1. 暗号化の有無を確認（エントロピー分析）
2. 一般的な圧縮形式を試す（zlib, lz4など）
3. より多くのサンプルパケットを収集して分析

## 参考リソース

### BPSR Logsのコード

[BPSR Logs GitHub](https://github.com/winjwinj/bpsr-logs) のコードを参照:
- パケットキャプチャの実装
- パケット構造の定義
- データ抽出ロジック

### ツール

- **Wireshark**: パケット解析の定番
- **HxD**: バイナリエディタ
- **010 Editor**: バイナリテンプレート機能付き
- **IDA Pro / Ghidra**: ゲームクライアントの解析（上級者向け）

## 注意事項

⚠️ **重要**: 
- パケット解析は教育目的とゲーム体験向上のためにのみ行ってください
- ゲームクライアントの逆アセンブルは利用規約違反になる可能性があります
- 他プレイヤーのパケットは解析しないでください（プライバシー侵害）
- 取得したデータは適切に管理してください

## 次のステップ

1. **パケットサンプルの収集**: 様々な状況でパケットをキャプチャ
2. **パターンの識別**: 取引所関連のパケットを特定
3. **パーサーの実装**: `src-tauri/src/packet_parser.rs` に実装
4. **テストとデバッグ**: 実際のゲームデータで検証
