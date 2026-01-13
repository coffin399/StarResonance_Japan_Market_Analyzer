# WinDivert セットアップガイド

## 必要なファイル

このプロジェクトでは以下のWinDivertファイルが必要です：

### 現在配置されているファイル
- ✅ `WinDivert.dll` (32-bit DLL)
- ✅ `WinDivert64.sys` (64-bit ドライバー)

### 追加で必要なファイル
- ⚠️ `WinDivert64.dll` (64-bit DLL) - **必須**
- ⚠️ `WinDivert.sys` (32-bit ドライバー) - オプション

## インストール手順

1. **WinDivertをダウンロード**
   - https://www.reqrypt.org/windivert.html
   - または https://github.com/basil00/Divert/releases

2. **ファイルを配置**
   
   ダウンロードしたZIPファイルから以下を抽出：
   ```
   WinDivert-2.2.2-A/x64/WinDivert.dll → src-tauri/WinDivert64.dll (リネーム)
   WinDivert-2.2.2-A/x64/WinDivert.sys → src-tauri/WinDivert64.sys
   WinDivert-2.2.2-A/x86/WinDivert.dll → src-tauri/WinDivert.dll
   WinDivert-2.2.2-A/x86/WinDivert.sys → src-tauri/WinDivert.sys
   ```

3. **ファイル構成を確認**
   ```
   src-tauri/
   ├── WinDivert.dll       (32-bit DLL)
   ├── WinDivert64.dll     (64-bit DLL) ← 追加必要
   ├── WinDivert.sys       (32-bit driver)
   └── WinDivert64.sys     (64-bit driver) ← 配置済み
   ```

## ビルド時の注意

- Rust は 64-bit ターゲットでビルドするため、`WinDivert64.dll` が必須
- ビルド時にこれらのファイルは自動的にバンドルに含まれます
- 実行時には管理者権限が必要です

## トラブルシューティング

### "WinDivert.dll が見つかりません"

**原因**: DLLファイルが正しく配置されていない

**解決策**:
1. `src-tauri` フォルダに `WinDivert64.dll` があることを確認
2. ファイル名が正確であることを確認（スペースや余分な文字がない）

### "WinDivertの開始に失敗"

**原因**: 管理者権限がない、またはドライバーがロードできない

**解決策**:
1. アプリを管理者権限で実行
2. アンチウイルスの除外設定に追加
3. Windowsのテストモードを有効化（署名のない ドライバーの場合）

### リンクエラー

**原因**: DLLのビット数が一致しない

**解決策**:
- 64-bit ビルドには `WinDivert64.dll` を使用
- 32-bit ビルドには `WinDivert.dll` を使用

## 開発モードでの実行

```bash
# 管理者権限でPowerShellを開く
# プロジェクトディレクトリに移動
cd path/to/StarResonance_Japan_Market_Analyzer

# 開発モードで起動
npm run tauri:dev
```

## リリースビルド

```bash
# リリースビルド
npm run tauri:build

# ビルド成果物の場所
# src-tauri/target/release/StarResonance-Market-Analyzer.exe
```

リリースビルド時、WinDivertファイルは自動的に実行ファイルと同じフォルダにコピーされます。
