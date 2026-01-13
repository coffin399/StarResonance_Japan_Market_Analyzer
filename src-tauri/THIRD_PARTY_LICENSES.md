# サードパーティライセンス

このプロジェクトは以下のサードパーティライブラリを使用しています。

## WinDivert

### プロジェクト情報
- **プロジェクト名**: WinDivert
- **著作権**: Copyright (c) 2012-2022 Basil
- **ウェブサイト**: https://www.reqrypt.org/windivert.html
- **GitHub**: https://github.com/basil00/Divert
- **バージョン**: 2.2.2-A

### ライセンス

WinDivertはデュアルライセンスで提供されています:

#### オプション 1: GNU Lesser General Public License (LGPL) Version 3

このプロジェクトではLGPL v3の下でWinDivertを使用しています。

```
                   GNU LESSER GENERAL PUBLIC LICENSE
                       Version 3, 29 June 2007

 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

[... 全文は https://www.gnu.org/licenses/lgpl-3.0.txt を参照]
```

#### オプション 2: MIT License

```
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 使用方法
- WinDivertは動的リンクライブラリ (DLL) として使用されます
- このプロジェクトではWinDivertのソースコードを変更していません
- バイナリファイル (`WinDivert.dll`, `WinDivert64.dll`, `WinDivert.sys`, `WinDivert64.sys`) をそのまま使用しています

### 配布に含まれるファイル
- `WinDivert.dll` - 32-bit ユーザーモードライブラリ
- `WinDivert64.dll` - 64-bit ユーザーモードライブラリ
- `WinDivert.sys` - 32-bit カーネルモードドライバー
- `WinDivert64.sys` - 64-bit カーネルモードドライバー

---

## その他のRustクレート

本プロジェクトで使用しているRustクレートのライセンス情報:

### Tauri
- **ライセンス**: MIT OR Apache-2.0
- **説明**: デスクトップアプリケーションフレームワーク

### Tokio
- **ライセンス**: MIT
- **説明**: 非同期ランタイム

### Serde
- **ライセンス**: MIT OR Apache-2.0
- **説明**: シリアライゼーションフレームワーク

### SQLite (rusqlite)
- **ライセンス**: MIT
- **説明**: SQLiteデータベースバインディング

### Chrono
- **ライセンス**: MIT OR Apache-2.0
- **説明**: 日付・時刻処理ライブラリ

### Anyhow
- **ライセンス**: MIT OR Apache-2.0
- **説明**: エラーハンドリングライブラリ

### Tracing
- **ライセンス**: MIT
- **説明**: ロギングフレームワーク

### Etherparse
- **ライセンス**: MIT OR Apache-2.0
- **説明**: ネットワークパケットパーサー

### Pnet
- **ライセンス**: MIT OR Apache-2.0
- **説明**: ネットワークライブラリ

---

## NPMパッケージ

### Svelte
- **ライセンス**: MIT
- **説明**: リアクティブUIフレームワーク

### Vite
- **ライセンス**: MIT
- **説明**: ビルドツール

### その他のパッケージ
本プロジェクトで使用しているその他のNPMパッケージはすべてMITライセンスです。
詳細は `package.json` を参照してください。

---

## ライセンス互換性

すべてのサードパーティライブラリはAGPL-3.0と互換性があります:

- **LGPL v3**: AGPL-3.0と互換（動的リンクで使用）
- **MIT**: AGPL-3.0と互換
- **Apache-2.0**: AGPL-3.0と互換

---

## 完全なライセンステキスト

### LGPL v3
https://www.gnu.org/licenses/lgpl-3.0.txt

### MIT License
https://opensource.org/licenses/MIT

### Apache License 2.0
https://www.apache.org/licenses/LICENSE-2.0

---

**注意**: このファイルは情報提供のみを目的としています。
各ライブラリの正確なライセンス条項については、それぞれの公式ドキュメントを参照してください。
