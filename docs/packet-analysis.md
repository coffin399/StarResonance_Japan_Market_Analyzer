# パケット解析ガイド

このガイドでは、Wiresharkを使用してゲームのトレーディングセンターパケットをキャプチャし、解析する方法を説明します。

## 前提条件

- Wireshark（最新版推奨）
- ブループロトコル:スターレゾナンス がインストールされている
- 基本的なネットワーク知識

## 重要な注意事項

⚠️ **このツールはパケット解析のみを行います**

- ゲームクライアントへの干渉や改変は一切行いません
- 読み取り専用のトラフィック監視です
- 運営から不正ツールに該当しないとの判断を得ています
- ただし、自己責任で使用してください

## 1. Wiresharkのインストール

### Windows

1. [Wireshark公式サイト](https://www.wireshark.org/download.html) からインストーラーをダウンロード
2. インストーラーを実行し、デフォルト設定でインストール
3. Npcap（パケットキャプチャドライバ）も一緒にインストールされます

### インストール確認

コマンドプロンプトまたはPowerShellで:

```powershell
# Wiresharkのバージョン確認
tshark -v
```

## 2. ゲームサーバーの特定

### 方法1: Wiresharkで手動確認

1. Wiresharkを起動
2. 使用しているネットワークインターフェース（Wi-Fiまたはイーサネット）を選択
3. キャプチャを開始
4. ゲームを起動してログイン
5. 取引所にアクセス
6. Wiresharkでトラフィックを確認し、ゲームサーバーのIPアドレスを特定

### 方法2: タスクマネージャー（Windows 11）

1. タスクマネージャーを開く（Ctrl+Shift+Esc）
2. パフォーマンスタブ → リソースモニターを開く
3. ネットワークタブでゲームプロセスを探す
4. 接続先アドレスを確認

## 3. パケットキャプチャの設定

### キャプチャフィルタの設定

Wiresharkで以下のキャプチャフィルタを設定:

```
host [GAME_SERVER_IP]
```

例:
```
host 192.168.1.100
```

または、特定のポートでフィルタ:
```
tcp port 12345 and host [GAME_SERVER_IP]
```

### ディスプレイフィルタ

キャプチャ後、以下のディスプレイフィルタで取引所パケットを絞り込み:

```
tcp contains "c3SB"
```

これは取引所パケットのマジックバイト `00 63 33 53 42 00` を検索します。

## 4. 取引所パケットのキャプチャ

### 手順

1. Wiresharkでキャプチャを開始
2. ゲームを起動
3. 取引所にアクセス
4. 出品リストを表示
5. アイテムを検索
6. いくつかのアイテムを確認
7. Wiresharkでキャプチャを停止

### ファイルの保存

1. File → Save As...
2. ファイル名: `trading_capture_YYYYMMDD.pcap`
3. 保存先: プロジェクトの `pcaps/` フォルダ

## 5. パケット構造の理解

### 取引所パケットの基本構造

```
[ヘッダー][マジックバイト][データ長][リスティング情報...]
```

#### マジックバイト
```
00 63 33 53 42 00
```

このバイト列が取引所パケットの開始を示します。

#### リスティング情報（推定）
```
[リスティングID: 8 bytes]
[アイテムID: 4 bytes]
[数量: 4 bytes]
[価格: 8 bytes]
[アイテム名長: 2 bytes]
[アイテム名: N bytes (UTF-8)]
[出品者情報...]
```

**注意**: 実際のパケット構造は異なる可能性があります。デコーダーの実装は要調整です。

## 6. デコーダーの使用

### 基本的な使い方

```python
from src.packet_decoder import TradingCenterDecoder

# Pcapファイルを読み込んで解析
decoder = TradingCenterDecoder("pcaps/trading_capture.pcap")
packets = decoder.decode_pcap_file()

print(f"デコードしたパケット数: {len(packets)}")

# 各パケットの情報を表示
for packet in packets:
    if packet.listings:
        for listing in packet.listings:
            print(f"アイテム: {listing.item_name}")
            print(f"  価格: {listing.price}")
            print(f"  数量: {listing.quantity}")
```

### リアルタイムキャプチャ

Scapyを使用してリアルタイムでパケットをキャプチャすることもできます:

```python
from scapy.all import sniff
from src.packet_decoder import TradingCenterDecoder

decoder = TradingCenterDecoder()

def packet_callback(packet):
    if packet.haslayer('Raw'):
        payload = bytes(packet['Raw'].load)
        trading_packet = decoder.decode_from_bytes(payload)
        if trading_packet and trading_packet.listings:
            for listing in trading_packet.listings:
                print(f"新しい出品: {listing.item_name} @ {listing.price}")

# キャプチャ開始（管理者権限が必要）
sniff(filter="tcp and host [GAME_SERVER_IP]", prn=packet_callback)
```

## 7. データベースへの保存

デコードしたデータをデータベースに保存:

```python
from src.packet_decoder import TradingCenterDecoder
from src.database import SessionLocal, Item, Listing

# デコード
decoder = TradingCenterDecoder("pcaps/trading_capture.pcap")
packets = decoder.decode_pcap_file()

# データベースセッション
db = SessionLocal()

try:
    for packet in packets:
        if packet.listings:
            for listing_data in packet.listings:
                # アイテムを取得または作成
                item = db.query(Item).filter(Item.id == listing_data.item_id).first()
                if not item:
                    item = Item(
                        id=listing_data.item_id,
                        name=listing_data.item_name
                    )
                    db.add(item)
                
                # リスティングを保存
                listing = Listing(
                    id=int(listing_data.listing_id),
                    item_id=listing_data.item_id,
                    quantity=listing_data.quantity,
                    price=listing_data.price,
                    unit_price=listing_data.price // listing_data.quantity if listing_data.quantity > 0 else listing_data.price,
                    seller_name=listing_data.seller_name,
                    captured_at=listing_data.timestamp
                )
                db.add(listing)
    
    db.commit()
    print("データベースに保存しました")
except Exception as e:
    db.rollback()
    print(f"エラー: {e}")
finally:
    db.close()
```

## 8. トラブルシューティング

### パケットがキャプチャできない

**原因**: 
- 間違ったネットワークインターフェースを選択している
- ゲームが暗号化通信を使用している
- ファイアウォールがブロックしている

**解決策**:
- 正しいインターフェースを選択
- すべてのインターフェースでキャプチャを試す
- Npcapを再インストール

### マジックバイトが見つからない

**原因**:
- パケット構造が変更された
- 取引所以外のパケットをキャプチャしている

**解決策**:
- 16進数ビューで手動でパターンを探す
- Wiresharkの「Find Packet」機能を使用
- ゲームアップデート後はパケット構造の再調査が必要

### デコードエラー

**原因**:
- パケット構造の推定が間違っている
- エンディアンの間違い
- データ型の不一致

**解決策**:
- `decoder.py` のオフセットとデータ型を調整
- 複数のパケットを比較して構造を特定
- バイナリエディタで手動確認

## 9. ベストプラクティス

### キャプチャのタイミング

- ゲーム起動直後（ログインパケットを含める）
- 取引所で様々な操作を実行
- 出品、検索、購入など異なるアクションを試す

### ファイル管理

```
pcaps/
├── trading_capture_20260128_morning.pcap
├── trading_capture_20260128_evening.pcap
└── README.txt  # キャプチャ時のメモ
```

### セキュリティ

- Pcapファイルには個人情報が含まれる可能性があります
- 公開する際は匿名化を検討
- `.gitignore` に `pcaps/` を追加済み

## 10. 参考資料

- [Wireshark公式ドキュメント](https://www.wireshark.org/docs/)
- [Scapy公式ドキュメント](https://scapy.readthedocs.io/)
- [参考リポジトリ: bpsr_labs](https://github.com/JordieB/bpsr_labs)

## よくある質問

### Q: これは不正ツールではないですか？

A: パケット解析（読み取り専用の監視）は運営から不正ツールに該当しないとの判断を得ています。ただし、以下は禁止されています:
- ゲームクライアントの改変
- パケットの送信・改ざん
- 自動化された取引

### Q: バンされるリスクはありますか？

A: パケット解析自体は読み取り専用でゲームに干渉しないため、理論上リスクは低いです。ただし、自己責任で使用してください。

### Q: パケット構造が変わったらどうすればいいですか？

A: ゲームアップデート後は、再度パケットをキャプチャして構造を確認し、デコーダーを更新する必要があります。
