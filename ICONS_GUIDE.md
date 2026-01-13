# アイコン作成ガイド / Icon Creation Guide

## 🎨 必要なアイコンファイル

Tauriアプリケーションには以下のアイコンファイルが必要です：

```
src-tauri/icons/
├── 32x32.png        # 32x32 PNG
├── 128x128.png      # 128x128 PNG
├── 128x128@2x.png   # 256x256 PNG (Retina用)
├── icon.png         # 512x512 PNG (メイン)
└── icon.ico         # Windows用 ICOファイル（必須）
```

## ❌ 現在のエラー

```
`icons/icon.ico` not found; required for generating a Windows Resource file
```

このエラーは `icon.ico` ファイルが見つからないために発生しています。

## 🚀 クイックフィックス（3つの方法）

### 方法1: オンラインツールを使用（最も簡単）⭐

1. **Icon Kitchenを使用**
   - https://icon.kitchen/ にアクセス
   - 「Upload Image」をクリック
   - 512x512以上の画像をアップロード
   - 「Download」ボタンをクリック
   - ダウンロードしたZIPを解凍
   - `icons`フォルダの内容を `src-tauri/icons/` にコピー

2. **または Convertio を使用**
   - https://convertio.co/png-ico/
   - PNG画像をICOに変換
   - 複数サイズを含めるオプションを選択

### 方法2: PowerShellスクリプトを使用

#### A. シンプルなアイコンを自動生成

```powershell
# PowerShellを管理者として実行
.\create-simple-icon.ps1
```

このスクリプトは：
- SVGアイコンを自動生成
- Inkscapeがあれば自動的にPNG/ICOに変換
- なければ手動変換の手順を表示

#### B. 自分の画像から生成

```powershell
# 1. 画像を用意（1024x1024推奨）
# プロジェクトルートに app-icon-source.png として保存

# 2. スクリプトを実行
.\generate-icons.ps1
```

必要なツール：
- **ImageMagick**: https://imagemagick.org/script/download.php

### 方法3: 手動で作成

#### ステップ1: デザインツールで作成

以下のいずれかを使用：
- **Canva** (オンライン): https://www.canva.com/
- **Figma** (オンライン): https://www.figma.com/
- **GIMP** (無料): https://www.gimp.org/
- **Photoshop** (有料)
- **Paint.NET** (Windows無料): https://www.getpaint.net/

#### ステップ2: サイズを作成

| ファイル名 | サイズ | 用途 |
|-----------|--------|------|
| icon.png | 512x512 | メインアイコン |
| 128x128@2x.png | 256x256 | Retina表示 |
| 128x128.png | 128x128 | 標準表示 |
| 32x32.png | 32x32 | 小アイコン |

#### ステップ3: ICOファイルを作成

**オンライン変換ツール:**
- https://convertio.co/png-ico/
- https://cloudconvert.com/png-to-ico
- https://www.icoconverter.com/

**または ImageMagick（コマンドライン）:**
```bash
magick convert icon.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

#### ステップ4: ファイルを配置

```
src-tauri/icons/
├── 32x32.png
├── 128x128.png
├── 128x128@2x.png
├── icon.png
└── icon.ico  ← これが必須！
```

## 🎨 デザインガイドライン

### 推奨事項

✅ **良いアイコンデザイン:**
- シンプルで認識しやすい
- 小さいサイズでもはっきり見える
- 明るく特徴的な色を使用
- 透明な背景（PNG）
- 正方形（1:1の比率）

❌ **避けるべきこと:**
- 複雑すぎる詳細
- 細い線（小サイズで見えなくなる）
- 薄い色や低コントラスト
- テキストの多用

### アイコンのアイデア

StarResonance Market Analyzer に適したアイコン:
- ⭐ 星のマーク（Star Resonance）
- 📊 グラフ/チャート（Market Analyzer）
- 💰 コイン/お金
- 📈 上昇トレンドライン
- 🏪 店舗/マーケット
- 🔮 クリスタル/宝石

## 📦 使用可能なアイコンリソース

### 無料アイコン素材

1. **Flaticon**
   - https://www.flaticon.com/
   - 無料アイコン多数（要クレジット表記）

2. **Icons8**
   - https://icons8.com/
   - 様々なスタイルのアイコン

3. **Ionicons**
   - https://ionic.io/ionicons
   - オープンソース、MITライセンス

4. **Material Design Icons**
   - https://fonts.google.com/icons
   - Google製、Apacheライセンス

### カスタムアイコン作成サービス

1. **Fiverr**
   - カスタムアイコンデザイン（有料）
   - https://www.fiverr.com/

2. **99designs**
   - プロフェッショナルなデザイン（有料）
   - https://99designs.com/

## 🔧 トラブルシューティング

### "icon.ico not found" エラー

**原因:** `src-tauri/icons/icon.ico` が存在しない

**解決策:**
1. オンラインツールで作成（方法1）
2. スクリプトを実行（方法2）
3. 手動で作成（方法3）

### ICOファイルが正しく認識されない

**原因:** ICOファイルが破損しているか、形式が正しくない

**解決策:**
```powershell
# ImageMagickで再生成
magick convert icon.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

### アイコンがぼやける

**原因:** 元画像の解像度が低い

**解決策:**
- 1024x1024以上の高解像度画像を使用
- ベクター形式（SVG）から変換

### ビルド時にアイコンが更新されない

**原因:** キャッシュが残っている

**解決策:**
```batch
# キャッシュをクリア
clean.bat

# 再ビルド
build.bat
```

## 📋 チェックリスト

ビルド前に以下を確認：

- [ ] `src-tauri/icons/icon.ico` が存在する
- [ ] `src-tauri/icons/icon.png` が存在する（512x512）
- [ ] `src-tauri/icons/128x128.png` が存在する
- [ ] `src-tauri/icons/128x128@2x.png` が存在する（256x256）
- [ ] `src-tauri/icons/32x32.png` が存在する
- [ ] すべてのアイコンが正方形である
- [ ] アイコンが見やすく認識しやすい

## 🚀 クイックスタート

### 今すぐビルドしたい場合

一時的なアイコンを使用してビルド：

```powershell
# 1. シンプルなアイコンを自動生成
.\create-simple-icon.ps1

# 2. 生成されたSVGをオンラインで変換
# https://icon.kitchen/ にアップロード

# 3. ダウンロードしたアイコンを配置
# icons/* を src-tauri/icons/ にコピー

# 4. ビルド
.\build.bat
```

後で好きなデザインに差し替えることができます。

## 📚 参考リンク

- **Tauri Icons Guide**: https://tauri.app/v1/guides/features/icons
- **Icon Design Best Practices**: https://developer.apple.com/design/human-interface-guidelines/app-icons
- **Windows Icon Guidelines**: https://learn.microsoft.com/en-us/windows/apps/design/style/iconography/app-icon-construction

---

**ヒント:** 最も簡単なのは https://icon.kitchen/ を使うことです！
