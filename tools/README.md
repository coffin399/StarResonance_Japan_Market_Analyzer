# パケット解析ツール

このフォルダには、ゲームパケットを解析するための専用ツールが含まれています。

## ファイル一覧

### 1. packet_parser.py
ゲームパケット専用パーサー。Wiresharkでキャプチャしたpcapファイルを解析します。

**特徴:**
- 複数のマジックバイトパターンに対応
- Scapy未インストールでも動作
- 日本語アイテム名の自動検出
- JSON形式で結果を出力

### 2. parse-pcap.bat
pcapファイルを簡単に解析するバッチファイル。

**使い方:**
```bat
parse-pcap.bat capture.pcap
```

または、pcapファイルをバッチファイルにドラッグ&ドロップ！

### 3. analyze-traffic.bat
インタラクティブなトラフィック解析ツール。

**機能:**
- 既存pcapファイルの解析
- ネットワークインターフェース一覧表示
- リアルタイムキャプチャ
- マジックバイト検索

## 使い方

### 基本的な使い方

1. **Wiresharkでパケットをキャプチャ**
   ```
   フィルタ: tcp
   キャプチャ時間: ゲームで取引所を開いている間
   ```

2. **pcapファイルとして保存**
   ```
   File → Save As → capture.pcap
   ```

3. **パーサーで解析**
   ```bat
   parse-pcap.bat capture.pcap
   ```

### 高度な使い方

#### オプション1: Pythonから直接実行

```python
from tools.packet_parser import GamePacketParser

parser = GamePacketParser('capture.pcap')
items = parser.parse()

for item in items:
    print(f"{item['item_name']}: {item['price']:,}円")

parser.save_results('output.json')
```

#### オプション2: インタラクティブツール

```bat
analyze-traffic.bat
```

メニューから選択:
1. 既存pcapを解析
2. ネットワークインターフェース確認
3. リアルタイムキャプチャ（要管理者権限）
4. マジックバイト検索

## 出力形式

### コンソール出力

```
==========================================
RESULTS
==========================================
Total packets: 1523
Trading packets: 12
Items found: 47

Sample items:
  - 高級素材: 10x @ 10,000 (unit: 1,000)
  - レアな鉱石: 5x @ 25,000 (unit: 5,000)
  ...

Full results saved to: parsed_items_20260128_123456.json
```

### JSON出力

```json
{
  "pcap_file": "capture.pcap",
  "parsed_at": "2026-01-28T12:34:56",
  "total_packets": 1523,
  "trading_packets": 12,
  "items_found": 47,
  "items": [
    {
      "listing_id": 123456789,
      "item_id": 1001,
      "item_name": "高級素材",
      "quantity": 10,
      "price": 10000,
      "unit_price": 1000
    },
    ...
  ]
}
```

## トラブルシューティング

### Q: "No items found"と表示される

**A:** 以下を確認してください:

1. **正しいタイミングでキャプチャしているか**
   - ゲームを起動
   - 取引所を開く
   - 出品リストを表示
   - アイテムを検索

2. **正しいネットワークインターフェースか**
   ```bat
   analyze-traffic.bat → オプション2
   ```
   で確認

3. **ゲームサーバーのIPアドレスを特定**
   - Wiresharkで Statistics → Conversations → TCP
   - 最も通信量の多い接続を確認

### Q: "Scapy is not installed"と表示される

**A:** Scapyは必須ではありません。なくても動作します。

インストールする場合:
```bash
pip install scapy
```

Windowsの場合、Npcapも必要:
- Wiresharkをインストール（Npcap含む）
- または https://npcap.com/ から単独インストール

### Q: パケットは見つかるがアイテム名が文字化けする

**A:** エンコーディングの問題です。

`packet_parser.py` の以下を変更:
```python
item_name = data[offset:offset+name_length].decode('utf-8', errors='ignore')
```
↓
```python
# Shift-JIS を試す
item_name = data[offset:offset+name_length].decode('shift-jis', errors='ignore')
```

### Q: 解析は成功するが、価格や数量がおかしい

**A:** パケット構造の推定が間違っている可能性があります。

1. **デバッグモードで実行**
   ```bash
   python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
   python tools\packet_parser.py capture.pcap
   ```

2. **Wiresharkで手動確認**
   - 取引所パケットを特定
   - Follow TCP Stream
   - バイト列を確認
   - `packet_parser.py`のオフセットを調整

## パケット構造の解析方法

### ステップ1: マジックバイトを探す

```python
# 候補
magic = b'\x00\x63\x33\x53\x42\x00'  # 既知
magic = b'c3SB'                       # ASCII
```

### ステップ2: データ構造を推定

```
[Magic Bytes: 6 bytes]
[Count: 4 bytes]
  [Listing ID: 8 bytes]
  [Item ID: 4 bytes]
  [Quantity: 4 bytes]
  [Price: 8 bytes]
  [Name Length: 2 bytes]
  [Name: N bytes (UTF-8)]
  ...repeat...
```

### ステップ3: 検証

1. Wiresharkで実際のパケットを確認
2. `packet_parser.py`を調整
3. 再テスト

## 参考リンク

- [Wireshark](https://www.wireshark.org/)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [参考リポジトリ: JordieB/bpsr_labs](https://github.com/JordieB/bpsr_labs)
- [参考リポジトリ: winjwinj/bpsr-logs](https://github.com/winjwinj/bpsr-logs)

## サンプルワークフロー

```bat
REM 1. Wiresharkで60秒間キャプチャ
REM    (ゲームで取引所を操作)

REM 2. pcapとして保存
REM    File → Save As → capture.pcap

REM 3. 解析実行
parse-pcap.bat capture.pcap

REM 4. 結果確認
REM    parsed_items_YYYYMMDD_HHMMSS.json が生成される

REM 5. データベースにインポート（オプション）
python scripts\import_from_json.py parsed_items_20260128_123456.json
```

## ヒント

1. **キャプチャのタイミングが重要**
   - ログイン直後
   - 取引所を開いた瞬間
   - 検索実行時
   - ページ切り替え時

2. **フィルタの活用**
   ```
   tcp.port == [game_port]
   ip.addr == [game_server]
   tcp.len > 100
   ```

3. **複数回試す**
   - 1回で成功しないこともある
   - 異なるタイミングで複数キャプチャ
   - 結果を比較

4. **ログを確認**
   - パーサーはデバッグ情報を出力
   - 何が見つかったか確認
   - 構造の推定に役立つ
