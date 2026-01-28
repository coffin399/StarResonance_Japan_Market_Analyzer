# リアルタイムキャプチャガイド

このガイドでは、ゲーム実行中にリアルタイムでパケットをキャプチャする方法を説明します。

## 概要

リアルタイムキャプチャ機能を使用すると、以下が可能になります:

- ゲーム実行中に自動でパケットをキャプチャ
- 取引所の出品情報をリアルタイムで検出
- データベースへの自動保存
- WebSocketによるリアルタイム配信
- Wiresharkを使わずに直接キャプチャ

## 前提条件

### Windows

- **管理者権限**: パケットキャプチャには管理者権限が必要
- **WinPcap/Npcap**: Scapyが使用するパケットキャプチャドライバ
  - Wiresharkをインストールすると自動的にインストールされます
  - または単体でインストール: https://npcap.com/

### 必要なPythonパッケージ

```bash
pip install scapy websockets
```

## セットアップ

### 1. Npcapのインストール確認

```bash
# Scapyが正しく動作するか確認
python -c "from scapy.all import sniff; print('OK')"
```

エラーが出る場合は、Npcapを再インストールしてください。

### 2. 管理者権限で実行

パケットキャプチャには管理者権限が必要です。

#### コマンドプロンプトを管理者として実行

1. スタートメニューで「cmd」を検索
2. 右クリック → 「管理者として実行」
3. プロジェクトディレクトリに移動

```cmd
cd C:\Users\YourName\StarResonance_Japan_Market_Analyzer
venv\Scripts\activate
```

## 使用方法

### 方法1: Pythonスクリプト（最も簡単）

```bash
# 管理者権限のコマンドプロンプトで実行
python examples/realtime_capture_example.py
```

メニューから選択:
1. **基本キャプチャ**: コンソールに出力のみ
2. **データベース保存**: 自動でDBに保存
3. **フィルタ付き**: 特定サーバーのみキャプチャ

### 方法2: API経由（プログラマティック）

#### ステップ1: APIサーバーを起動

```bash
# 管理者権限で実行
python -m src.api.main
```

#### ステップ2: キャプチャを開始

```bash
curl -X POST http://localhost:8000/api/v1/realtime/start
```

または特定サーバーを指定:

```bash
curl -X POST "http://localhost:8000/api/v1/realtime/start?game_server_ip=192.168.1.100&game_server_port=12345"
```

#### ステップ3: ステータス確認

```bash
curl http://localhost:8000/api/v1/realtime/status
```

レスポンス例:
```json
{
  "is_running": true,
  "stats": {
    "total_packets": 1523,
    "trading_packets": 12,
    "listings_found": 47,
    "duration": 120.5
  },
  "connected_clients": 2
}
```

#### ステップ4: キャプチャを停止

```bash
curl -X POST http://localhost:8000/api/v1/realtime/stop
```

### 方法3: WebSocketでリアルタイム受信

Web UIやDiscord Botからリアルタイムでデータを受信できます。

#### JavaScript例

```javascript
// WebSocket接続を作成
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws');

ws.onopen = () => {
    console.log('Connected to real-time market data');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'new_listings') {
        console.log(`Received ${data.count} new listings:`);
        
        data.listings.forEach(listing => {
            console.log(`- ${listing.item_name}: ${listing.quantity}x @ ${listing.price}`);
        });
        
        // UIを更新
        updateMarketUI(data.listings);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected from real-time market data');
};
```

#### Python例（Discord Bot）

```python
import asyncio
import websockets
import json

async def receive_market_data():
    uri = "ws://localhost:8000/api/v1/realtime/ws"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to market data stream")
        
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'new_listings':
                # Discord channelに投稿
                listings = data['listings']
                message = f"**新着出品 {len(listings)}件**\n"
                
                for listing in listings[:5]:  # 最初の5件のみ
                    message += f"• {listing['item_name']}: {listing['quantity']}個 @ {listing['price']:,}円\n"
                
                await discord_channel.send(message)

# Botのイベントループで実行
asyncio.create_task(receive_market_data())
```

## Pythonコードでの使用

### 基本的な使用例

```python
from src.packet_decoder.realtime_capture import (
    RealtimePacketCapture,
    RealtimeCaptureCallback
)

# コールバッククラスを作成
class MyCallback(RealtimeCaptureCallback):
    def on_listing_found(self, listings):
        for listing in listings:
            print(f"New: {listing.item_name} @ {listing.price}")

# キャプチャを開始
callback = MyCallback()
capture = RealtimePacketCapture(callback=callback)
capture.start()

# 実行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    capture.stop()
```

### データベースへの自動保存

```python
from src.packet_decoder.realtime_capture import (
    RealtimePacketCapture,
    DatabaseCallback
)
from src.database import SessionLocal

# データベースセッション
db = SessionLocal()

# データベースコールバック
callback = DatabaseCallback(db)

# キャプチャを開始
capture = RealtimePacketCapture(callback=callback)
capture.start()

# 自動的にDBに保存される
```

### 複数コールバックの組み合わせ

```python
class CombinedCallback(RealtimeCaptureCallback):
    def __init__(self, db_session):
        self.console = ConsoleCallback()
        self.database = DatabaseCallback(db_session)
    
    def on_listing_found(self, listings):
        # コンソールに出力
        self.console.on_listing_found(listings)
        # データベースに保存
        self.database.on_listing_found(listings)

db = SessionLocal()
callback = CombinedCallback(db)
capture = RealtimePacketCapture(callback=callback)
capture.start()
```

## トラブルシューティング

### 問題: "Permission denied" エラー

**原因**: 管理者権限がない

**解決策**:
- コマンドプロンプトを「管理者として実行」
- または PowerShell を管理者として実行

### 問題: "No such device exists" エラー

**原因**: Npcapが正しくインストールされていない

**解決策**:
1. Npcapをアンインストール
2. Wiresharkをアンインストール
3. PCを再起動
4. Wiresharkを再インストール（Npcapも含まれる）

### 問題: パケットが検出されない

**原因**:
- ゲームサーバーのIPアドレスが間違っている
- ネットワークインターフェースが間違っている
- ゲームが暗号化通信を使用している

**解決策**:
1. Wiresharkで手動確認してサーバーIPを特定
2. すべてのインターフェースでキャプチャを試す
3. フィルタなしでキャプチャしてみる

```python
# フィルタなしでキャプチャ
capture = RealtimePacketCapture(
    callback=callback,
    game_server_ip=None,  # すべてのIPを監視
    game_server_port=None  # すべてのポートを監視
)
```

### 問題: メモリ使用量が増え続ける

**原因**: パケットキューが満杯

**解決策**: キャプチャを定期的に再起動するか、不要なパケットをフィルタ

## パフォーマンス最適化

### 1. 適切なフィルタを使用

```python
# ゲームサーバーのみを監視
capture = RealtimePacketCapture(
    game_server_ip="192.168.1.100",
    game_server_port=12345
)
```

### 2. コールバックを軽量に保つ

```python
class LightweightCallback(RealtimeCaptureCallback):
    def on_listing_found(self, listings):
        # 重い処理は別スレッドで実行
        threading.Thread(
            target=self.process_listings,
            args=(listings,)
        ).start()
    
    def process_listings(self, listings):
        # 時間のかかる処理
        pass
```

### 3. バッチ処理

```python
class BatchCallback(RealtimeCaptureCallback):
    def __init__(self):
        self.batch = []
        self.batch_size = 100
    
    def on_listing_found(self, listings):
        self.batch.extend(listings)
        
        if len(self.batch) >= self.batch_size:
            self.flush_batch()
    
    def flush_batch(self):
        # 一括でDBに保存
        save_to_database(self.batch)
        self.batch.clear()
```

## セキュリティとプライバシー

### データの取り扱い

- キャプチャしたパケットには個人情報が含まれる可能性があります
- `.gitignore` に `pcaps/` が含まれていることを確認
- 公開する場合は匿名化を検討

### 運営の方針

- パケット解析（読み取り専用）は運営から承認されています
- パケットの送信や改ざんは禁止
- 自動化された取引は禁止

## まとめ

リアルタイムキャプチャを使用することで:

✅ Wiresharkを開く必要がない  
✅ 自動でデータベースに保存  
✅ WebSocketでリアルタイム配信  
✅ Discord Botとの連携が簡単  
✅ バックグラウンドで実行可能  

詳細は [examples/realtime_capture_example.py](../examples/realtime_capture_example.py) を参照してください。
