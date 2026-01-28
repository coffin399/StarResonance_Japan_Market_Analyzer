# コントリビューションガイド

Star Resonance Market Analyzer への貢献に興味を持っていただきありがとうございます！

## 貢献の方法

### バグレポート

バグを見つけた場合は、GitHubのIssuesで報告してください。以下の情報を含めてください:

- 問題の詳細な説明
- 再現手順
- 期待される動作と実際の動作
- 環境情報（OS、Pythonバージョンなど）
- エラーメッセージやスタックトレース

### 機能リクエスト

新機能の提案も歓迎します！Issuesで以下を含めて説明してください:

- 機能の概要
- なぜその機能が必要か
- 想定される使用例

### プルリクエスト

1. **フォークとクローン**
   ```bash
   git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
   cd StarResonance_Japan_Market_Analyzer
   ```

2. **ブランチを作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **開発環境のセットアップ**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

4. **変更を実装**
   - コードスタイルガイドに従う
   - テストを追加/更新
   - ドキュメントを更新

5. **テストを実行**
   ```bash
   pytest
   ```

6. **コミット**
   ```bash
   git add .
   git commit -m "Add: 新機能の説明"
   ```

7. **プッシュしてPRを作成**
   ```bash
   git push origin feature/your-feature-name
   ```

## コードスタイル

### Python

- [PEP 8](https://peps.python.org/pep-0008/) に従う
- Black でフォーマット: `black src/`
- Flake8 でリント: `flake8 src/`
- 型ヒントを使用（可能な限り）

### コミットメッセージ

以下のプレフィックスを使用:

- `Add:` - 新機能の追加
- `Fix:` - バグ修正
- `Update:` - 既存機能の更新
- `Refactor:` - リファクタリング
- `Docs:` - ドキュメントの変更
- `Test:` - テストの追加/変更
- `Style:` - コードスタイルの変更

例:
```
Add: 価格アラート機能を追加
Fix: データベース接続エラーを修正
Update: API レスポンス形式を改善
```

## 開発ガイドライン

### パケットデコーダー

- `src/packet_decoder/decoder.py` を編集する場合は、実際のパケットでテスト
- 新しいパケットタイプを追加する場合は、`packet_types.py` にデータ構造を定義

### API

- 新しいエンドポイントは `src/api/routes/` に追加
- `schemas.py` にリクエスト/レスポンススキーマを定義
- OpenAPI ドキュメントが自動生成されることを確認

### データベース

- モデルの変更は `src/database/models.py`
- マイグレーションが必要な場合は Alembic を使用
- インデックスを適切に設定

### フロントエンド

- `web/templates/` にHTMLテンプレート
- `web/static/css/` にスタイル
- `web/static/js/` にJavaScript
- レスポンシブデザインを維持

## テスト

### ユニットテスト

```python
# tests/test_profit_analyzer.py
import pytest
from src.analyzer import ProfitAnalyzer

def test_calculate_profit():
    analyzer = ProfitAnalyzer(fee_rate=0.05)
    result = analyzer.calculate_profit(1000, 1500, 10)
    
    assert result['total_buy_cost'] == 10000
    assert result['profit'] > 0
```

### テストの実行

```bash
# すべてのテストを実行
pytest

# カバレッジレポート
pytest --cov=src tests/
```

## ドキュメント

- コードにはdocstringを記述
- 複雑な処理にはコメントを追加
- READMEやdocs/を更新

例:
```python
def calculate_profit(buy_price: int, sell_price: int, quantity: int) -> Dict:
    """
    取引の利益を計算します。
    
    Args:
        buy_price: 購入価格
        sell_price: 販売価格
        quantity: 数量
        
    Returns:
        計算結果を含む辞書
        
    Examples:
        >>> calculate_profit(1000, 1500, 10)
        {'profit': 4250, 'profit_rate': 42.5, ...}
    """
```

## レビュープロセス

1. PRを作成すると自動テストが実行されます
2. メンテナーがコードレビューを行います
3. 必要に応じて修正をリクエストします
4. 承認後、mainブランチにマージされます

## 行動規範

- 敬意を持って接する
- 建設的なフィードバックを提供する
- 多様性を尊重する
- オープンソースコミュニティの精神を大切にする

## ライセンス

このプロジェクトに貢献することで、あなたの貢献がMITライセンスの下でライセンスされることに同意したものとみなされます。

## 質問やサポート

質問がある場合は、以下の方法でお問い合わせください:

- GitHub Issues
- GitHub Discussions
- Discord サーバー（準備中）

ご協力ありがとうございます！
