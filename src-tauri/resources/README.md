# リソースファイル

このフォルダにはアプリケーションに同梱するリソースファイルを配置します。

## WinDivertドライバー

このアプリケーションはWinDivertを使用します。以下のファイルをこのフォルダに配置してください:

### 必要なファイル
- `WinDivert.dll` (32-bit)
- `WinDivert64.dll` (64-bit)
- `WinDivert.sys` (32-bit driver)
- `WinDivert64.sys` (64-bit driver)

### ダウンロード

WinDivertは以下からダウンロードできます:
https://www.reqrypt.org/windivert.html

### インストール手順

1. WinDivertをダウンロード
2. ZIPファイルを展開
3. 上記のファイルをこのフォルダにコピー

### 構造例

```
resources/
├── WinDivert.dll
├── WinDivert64.dll
├── WinDivert.sys
└── WinDivert64.sys
```

## 注意事項

- WinDivertファイルは `.gitignore` に含まれています
- ビルド時に自動的にバンドルに含まれます
- ユーザーは管理者権限で実行する必要があります
- アンチウイルスが誤検知する可能性があります
