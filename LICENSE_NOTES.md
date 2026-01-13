# ライセンス情報

## プロジェクトライセンス

このプロジェクトは **GNU Affero General Public License v3.0 (AGPL-3.0)** の下で公開されています。

## WinDivertのライセンス

WinDivert は以下のライセンスで提供されています:

### WinDivert License

```
Copyright (c) 2012-2022 Basil
All rights reserved.

WinDivert is dual-licensed under the terms of either:
1. GNU Lesser General Public License (LGPL) Version 3
2. MIT License
```

**使用ライセンス**: LGPL v3

## ライセンス互換性

### AGPL-3.0 と LGPL v3

- ✅ **互換性あり**: LGPL v3はAGPL-3.0と互換性があります
- ✅ LGPLライブラリは動的リンクで使用可能
- ✅ WinDivertはランタイムで動的にロードされる

### 要件

1. **WinDivertのLGPL通知**
   - WinDivertのライセンス表示が必要
   - このファイルで明示

2. **ソースコードの提供**
   - プロジェクトはオープンソース（GitHub公開）
   - AGPL要件を満たしている

3. **変更の開示**
   - すべての変更はGitで追跡
   - 改変版も同じライセンスで公開

## サードパーティライセンス

### WinDivert (LGPL v3)
- **プロジェクト**: https://github.com/basil00/Divert
- **ライセンス**: LGPL v3 または MIT
- **使用方法**: 動的リンク (runtime DLL)
- **変更**: なし（そのまま使用）

### その他の依存関係

#### Rust クレート
- `tokio` - MIT
- `serde` - MIT/Apache-2.0
- `tauri` - MIT/Apache-2.0
- `rusqlite` - MIT
- `chrono` - MIT/Apache-2.0
- `anyhow` - MIT/Apache-2.0
- `tracing` - MIT
- `etherparse` - MIT/Apache-2.0

すべてAGPL-3.0と互換性があります。

#### NPM パッケージ
- `svelte` - MIT
- `vite` - MIT
- すべてMITライセンス（AGPL互換）

## 配布時の注意

### バイナリ配布
1. WinDivertファイルを含める:
   - `WinDivert.dll`
   - `WinDivert64.dll`
   - `WinDivert.sys`
   - `WinDivert64.sys`

2. ライセンス表示:
   - このファイル (`LICENSE_NOTES.md`)
   - `LICENSE` (AGPL-3.0全文)
   - WinDivertライセンス

### ソースコード配布
- GitHubで公開
- すべての変更を含む
- ビルド手順を記載

## 商用利用

### AGPL-3.0の要件
- ✅ 商用利用可能
- ⚠️ ネットワーク越しの利用でもソース公開義務あり
- ⚠️ 改変版も同じライセンスで公開必須

### 注意事項
このプロジェクトをネットワークサービスとして提供する場合:
- ユーザーにソースコードを提供する必要があります
- 改変版も AGPL-3.0 で公開する必要があります

## FAQ

### Q: なぜAGPL-3.0を選んだのか？
A: 
- BPSR Logsとの互換性
- オープンソースの精神を保つ
- ネットワークサービス化の際のソース公開義務

### Q: WinDivertを含めても問題ないか？
A: 
- ✅ はい、LGPLは動的リンクで使用可能
- WinDivertのライセンス表示が必要
- 変更していないバイナリをそのまま使用

### Q: 商用利用できるか？
A: 
- ✅ はい、可能です
- ただしAGPLの要件（ソース公開等）を満たす必要があります

### Q: 将来Web APIを提供する場合は？
A: 
- Web APIもAGPL-3.0の対象
- APIを使うユーザーにソースコード提供義務
- これが損益計算サイトに最適

### Q: より寛容なライセンスに変更できるか？
A: 
- 可能ですが、AGPL-3.0の利点を失います
- MIT/Apacheに変更する場合、すべての貢献者の同意が必要
- WinDivertはLGPLのまま（変更不可）

## 推奨事項

### このライセンスのまま進める理由

1. **オープンソースコミュニティ**
   - 改変版も公開される
   - コミュニティの改善が還元される

2. **Web サービス対応**
   - 将来のWeb API提供に最適
   - ユーザーは常にソースにアクセス可能

3. **互換性**
   - WinDivert (LGPL) と互換
   - すべての依存関係と互換

### ライセンス変更を検討する場合

もし商用での柔軟性が必要な場合:
1. **デュアルライセンス**: AGPL-3.0 + 商用ライセンス
2. **GPL-3.0**: ネットワーク義務なし（AGPLより緩い）
3. **MIT**: 最も寛容（ただしBPSR Logsとの精神に反する）

## 結論

**現在のAGPL-3.0ライセンスは問題ありません！**

- ✅ WinDivertと互換性あり
- ✅ すべての依存関係と互換性あり
- ✅ オープンソースの精神を保つ
- ✅ 将来のWeb API提供に最適

このまま進めることをお勧めします。

---

**最終更新**: 2026-01-13
