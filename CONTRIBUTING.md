# コントリビューションガイド

StarResonance Japan Market Analyzerへの貢献に興味を持っていただき、ありがとうございます！

## 行動規範

このプロジェクトに参加するすべての人は、敬意を持って接することが期待されます。

## 貢献の方法

### バグ報告

バグを見つけた場合は、以下の情報を含めてIssueを作成してください:

- **タイトル**: 問題の簡潔な説明
- **環境**: OS、バージョン、その他関連情報
- **再現手順**: バグを再現するための手順
- **期待される動作**: 本来どう動くべきか
- **実際の動作**: 実際に何が起きたか
- **スクリーンショット**: 可能であれば添付

### 機能リクエスト

新しい機能を提案する場合は:

1. まず既存のIssueを確認
2. 重複がなければ新しいIssueを作成
3. 以下を含める:
   - 機能の説明
   - ユースケース
   - 可能であれば実装案

### プルリクエスト

1. **Forkとクローン**
   ```bash
   git clone https://github.com/yourusername/StarResonance_Japan_Market_Analyzer.git
   cd StarResonance_Japan_Market_Analyzer
   ```

2. **ブランチを作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **変更を加える**
   - コーディング規約に従う
   - 適切なコメントを追加
   - テストを書く（該当する場合）

4. **コミット**
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   ```

   コミットメッセージの規約:
   - `feat:` 新機能
   - `fix:` バグ修正
   - `docs:` ドキュメントのみの変更
   - `style:` コードの動作に影響しない変更（フォーマット等）
   - `refactor:` リファクタリング
   - `test:` テストの追加・修正
   - `chore:` ビルドプロセスや補助ツールの変更

5. **プッシュ**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **プルリクエストを作成**
   - 変更内容の説明を記載
   - 関連するIssue番号を記載（`Closes #123`）
   - スクリーンショットを追加（UI変更の場合）

## 開発ガイドライン

### コードスタイル

- **Rust**: `cargo fmt` でフォーマット
- **TypeScript/Svelte**: Prettierでフォーマット

```bash
# フォーマット実行
npm run format
cargo fmt
```

### テスト

変更を加えた場合は、テストを実行してください:

```bash
npm test
cd src-tauri && cargo test
```

### ドキュメント

- 新しい機能を追加した場合は、ドキュメントも更新してください
- コードのコメントは日本語または英語で記載

## プロジェクト構造の理解

詳細は [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) を参照してください。

## レビュープロセス

1. プルリクエストは少なくとも1人のメンテナーによってレビューされます
2. フィードバックに対応してください
3. すべてのチェックが通り、承認されるとマージされます

## 質問

わからないことがあれば、Issueで質問するか、Discordで聞いてください。

## ライセンス

このプロジェクトに貢献することで、あなたの貢献がMITライセンスの下でライセンスされることに同意したものとみなされます。
