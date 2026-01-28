# Star Resonance Market Analyzer - プロジェクト概要

## 🎯 プロジェクトの目的

ブループロトコル:スターレゾナンスのゲーム内取引所データをパケット解析により収集し、市場価格の分析、損益計算、トレンド分析などを提供する包括的なツールです。

## ✨ 主な機能

### 1. パケット解析
- Wiresharkでキャプチャしたゲームトラフィックを解析
- 取引所の出品情報を自動抽出
- アイテムID、名前、価格、数量などを取得

### 2. データ管理
- SQLite/PostgreSQLでデータを永続化
- アイテム情報、出品履歴、価格推移を記録
- 効率的なインデックスとクエリ最適化

### 3. 損益計算ツール
- 購入価格と販売価格から利益を自動計算
- 手数料（マンスリーカード対応）を考慮
- 損益分岐点や目標利益達成価格を算出
- 複数シナリオの比較

### 4. トレンド分析
- 価格の上昇/下降トレンドを検出
- ボラティリティ（価格変動率）の計算
- 急騰/急落の検出
- サポート・レジスタンスラインの特定

### 5. REST API
- FastAPIベースの高速なAPI
- 完全なOpenAPIドキュメント
- Discord Botなど外部ツールとの連携が容易

### 6. Webインターフェース
- モダンでレスポンシブなUI
- リアルタイムの市場概要
- トレンドアイテムの表示
- インタラクティブな損益計算ツール

### 7. 外部公開
- Cloudflare Tunnelによるポート開放不要の公開
- セキュアなアクセス
- Discord Botとの連携

## 📊 技術スタック

### バックエンド
- **Python 3.11**: メイン言語
- **FastAPI**: Webフレームワーク
- **SQLAlchemy**: ORM
- **Pydantic**: データバリデーション
- **Scapy**: パケット解析

### フロントエンド
- **HTML5/CSS3**: マークアップとスタイリング
- **JavaScript (ES6+)**: インタラクティブ機能
- **Chart.js**: データ可視化（将来実装）

### データベース
- **SQLite**: 開発・小規模運用
- **PostgreSQL**: 本番環境推奨

### インフラ
- **Docker**: コンテナ化
- **Docker Compose**: オーケストレーション
- **Cloudflare Tunnel**: 外部公開
- **Uvicorn**: ASGIサーバー

## 📁 プロジェクト構造

```
StarResonance_Japan_Market_Analyzer/
├── src/                          # ソースコード
│   ├── packet_decoder/           # パケット解析
│   ├── database/                 # データベース
│   ├── analyzer/                 # 分析ツール
│   ├── api/                      # REST API
│   └── config.py                 # 設定管理
├── web/                          # フロントエンド
│   ├── templates/                # HTMLテンプレート
│   └── static/                   # CSS, JavaScript
├── tests/                        # テストコード
├── docs/                         # ドキュメント
├── examples/                     # 使用例
├── scripts/                      # ユーティリティスクリプト
├── pcaps/                        # Pcapファイル保存場所
├── logs/                         # ログファイル
├── docker-compose.yml            # Docker設定
├── Dockerfile                    # Dockerイメージ
├── requirements.txt              # Python依存パッケージ
├── start.bat / start.sh          # 起動スクリプト
└── README.md                     # プロジェクト説明
```

## 🚀 クイックスタート

### Windows

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer

# スタートスクリプトを実行
start.bat
```

### Linux/macOS

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
cd StarResonance_Japan_Market_Analyzer

# スタートスクリプトを実行
chmod +x start.sh
./start.sh
```

### Docker

```bash
docker-compose up -d
```

ブラウザで http://localhost:8000 にアクセス！

## 📖 ドキュメント

| ドキュメント | 説明 |
|------------|------|
| [はじめに](docs/GETTING_STARTED.md) | 初心者向けセットアップガイド |
| [APIリファレンス](docs/api-reference.md) | API仕様と使用例 |
| [パケット解析](docs/packet-analysis.md) | Wiresharkを使った解析方法 |
| [Cloudflare Tunnel](docs/cloudflare-tunnel.md) | 外部公開の設定 |
| [アーキテクチャ](docs/ARCHITECTURE.md) | システム設計と技術詳細 |
| [コントリビューション](CONTRIBUTING.md) | 開発への参加方法 |

## 🎓 使用例

### Python APIの使用

```python
import requests

# 最新の出品情報を取得
response = requests.get('http://localhost:8000/api/v1/listings/latest/all')
listings = response.json()

for listing in listings[:5]:
    print(f"{listing['item_name']}: {listing['price']:,}円")

# 損益計算
profit_data = {
    "buy_price": 1000,
    "sell_price": 1500,
    "quantity": 10,
    "fee_rate": 0.05
}
response = requests.post('http://localhost:8000/api/v1/calculate-profit', json=profit_data)
result = response.json()
print(f"利益: {result['profit']:,}円 ({result['profit_rate']:.1f}%)")
```

### パケット解析

```python
from src.packet_decoder import TradingCenterDecoder

# Pcapファイルを解析
decoder = TradingCenterDecoder('pcaps/trading_capture.pcap')
packets = decoder.decode_pcap_file()

# 市場スナップショットを作成
snapshot = decoder.create_market_snapshot()
print(f"出品アイテム数: {snapshot.total_items}")

for listing in snapshot.listings[:10]:
    print(f"{listing.item_name}: {listing.quantity}個 @ {listing.price:,}円")
```

### 損益分析

```python
from src.analyzer import ProfitAnalyzer

analyzer = ProfitAnalyzer(fee_rate=0.05, has_monthly_card=True)

# 利益計算
result = analyzer.calculate_profit(1000, 1500, 10)
print(f"純利益: {result['profit']:,}円")
print(f"利益率: {result['profit_rate']:.2f}%")

# 損益分岐点
break_even = analyzer.calculate_break_even_price(1000)
print(f"損益分岐点: {break_even:,}円")
```

## 🔒 セキュリティとコンプライアンス

### パケット解析について

- ✅ **読み取り専用**: ゲームトラフィックの監視のみ
- ✅ **非侵襲的**: クライアントへの干渉なし
- ✅ **パッシブ**: パケットの送信や改ざんなし
- ✅ **運営承認済み**: 不正ツールに該当しないとの判断

### 推奨される使用方法

- 市場価格の調査と分析
- 取引の損益計算
- トレンドの把握
- 個人的な取引記録の管理

### 禁止事項

- ❌ ゲームクライアントの改変
- ❌ パケットの送信・改ざん
- ❌ 自動化された取引
- ❌ 不正な利益の追求

## 🤝 コミュニティ

### 貢献方法

1. リポジトリをフォーク
2. 新しいブランチを作成
3. 変更をコミット
4. プルリクエストを作成

詳細は [CONTRIBUTING.md](CONTRIBUTING.md) を参照。

### バグ報告・機能リクエスト

GitHub Issuesで報告してください。

### ディスカッション

- GitHub Discussions
- Discord サーバー（準備中）

## 📈 ロードマップ

### v1.1 (近日予定)

- [ ] WebSocket対応（リアルタイムデータ）
- [ ] チャート可視化機能
- [ ] エクスポート機能（CSV, JSON）
- [ ] 価格アラート機能

### v1.2

- [ ] ユーザー認証
- [ ] お気に入りアイテム機能
- [ ] 取引履歴の記録
- [ ] モバイルアプリ対応

### v2.0

- [ ] 機械学習による価格予測
- [ ] 高度な分析ツール
- [ ] マルチ言語対応
- [ ] クラスタリング対応

## 📜 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照

## 🙏 謝辞

- [JordieB/bpsr_labs](https://github.com/JordieB/bpsr_labs) - パケット解析の参考実装
- ブループロトコル:スターレゾナンス コミュニティ
- すべてのコントリビューター

## 📞 お問い合わせ

- GitHub Issues: バグ報告・機能リクエスト
- GitHub Discussions: 一般的な質問
- Email: (準備中)

---

**Star Resonance Market Analyzer** - より良い取引体験を 🌟
