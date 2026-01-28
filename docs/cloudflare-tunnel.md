# Cloudflare Tunnel セットアップガイド

このガイドでは、Cloudflare Tunnelを使用してポート開放なしで市場解析ツールを外部公開する方法を説明します。

## 前提条件

- Cloudflareアカウント（無料プランで可）
- ドメイン（Cloudflare管理下、オプション）
- Windows/Linux/macOS

## 1. Cloudflared のインストール

### Windows

PowerShellで以下を実行:

```powershell
# インストーラーをダウンロード
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"

# システムパスに移動（管理者権限が必要）
Move-Item cloudflared.exe C:\Windows\System32\cloudflared.exe
```

### Linux/macOS

```bash
# Linux (Debian/Ubuntu)
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# macOS (Homebrew)
brew install cloudflared
```

## 2. Cloudflare にログイン

```bash
cloudflared tunnel login
```

ブラウザが開くので、Cloudflareアカウントでログインし、使用するドメインを選択します。

## 3. トンネルの作成

```bash
# トンネルを作成
cloudflared tunnel create bpsr-market

# 作成されたトンネルIDを確認
cloudflared tunnel list
```

トンネルが作成されると、認証ファイル（.json）が保存されます:
- Windows: `C:\Users\<USERNAME>\.cloudflared\`
- Linux/macOS: `~/.cloudflared/`

## 4. 設定ファイルの作成

プロジェクトのルートディレクトリに `cloudflare-tunnel-config.yml` を作成:

```yaml
tunnel: <TUNNEL_ID>  # tunnel list で確認したID
credentials-file: C:\Users\<USERNAME>\.cloudflared\<TUNNEL_ID>.json

ingress:
  # メインのWebアプリケーション
  - hostname: bpsr-market.yourdomain.com
    service: http://localhost:8000
  
  # API専用（オプション）
  - hostname: api.bpsr-market.yourdomain.com
    service: http://localhost:8000
    
  # すべての他のリクエストを404に
  - service: http_status:404
```

**重要**: 
- `<TUNNEL_ID>` を実際のトンネルIDに置き換えてください
- `<USERNAME>` をWindowsのユーザー名に置き換えてください
- `yourdomain.com` を実際のドメインに置き換えてください

## 5. DNS レコードの設定

トンネルとホスト名をマッピング:

```bash
# DNSレコードを追加
cloudflared tunnel route dns bpsr-market bpsr-market.yourdomain.com
cloudflared tunnel route dns bpsr-market api.bpsr-market.yourdomain.com
```

## 6. トンネルの起動

### 一時的に起動（テスト用）

```bash
cloudflared tunnel --config cloudflare-tunnel-config.yml run bpsr-market
```

### Windowsサービスとしてインストール（推奨）

管理者権限でPowerShellを開き:

```powershell
# サービスとしてインストール
cloudflared service install

# 設定ファイルのパスを設定
# デフォルト設定ファイルにコピー
Copy-Item cloudflare-tunnel-config.yml C:\Windows\System32\config\systemprofile\.cloudflared\config.yml

# サービスを開始
Start-Service cloudflared

# サービスの状態を確認
Get-Service cloudflared
```

### Linuxでsystemdサービスとして設定

```bash
# サービスとしてインストール
sudo cloudflared service install

# 設定ファイルを配置
sudo cp cloudflare-tunnel-config.yml /etc/cloudflared/config.yml

# サービスを有効化して起動
sudo systemctl enable cloudflared
sudo systemctl start cloudflared

# ステータス確認
sudo systemctl status cloudflared
```

## 7. クイックトンネル（開発用）

ドメイン設定なしで即座にテストする場合:

```bash
# APIサーバーを起動（別のターミナル）
python -m src.api.main

# クイックトンネルを起動
cloudflared tunnel --url http://localhost:8000
```

ランダムなURLが生成されます（例: `https://random-word-1234.trycloudflare.com`）

## 8. トンネルの確認

ブラウザで以下にアクセスして確認:

```
https://bpsr-market.yourdomain.com
https://bpsr-market.yourdomain.com/api/docs
```

## トラブルシューティング

### トンネルが起動しない

```bash
# ログを確認
cloudflared tunnel info bpsr-market

# Windows: イベントビューアーでcloudflaredサービスのログを確認
# Linux: journalctl -u cloudflared -f
```

### APIサーバーに接続できない

- APIサーバーが `0.0.0.0:8000` でリッスンしているか確認
- ファイアウォールでポート8000がブロックされていないか確認（ローカルホストの場合は通常問題なし）

### DNS伝搬の待機

DNSレコードの変更は最大48時間かかる場合があります。すぐに確認したい場合:

```bash
# DNSキャッシュをクリア
# Windows
ipconfig /flushdns

# Linux
sudo systemd-resolve --flush-caches

# macOS
sudo dscacheutil -flushcache
```

## セキュリティ設定（推奨）

### Cloudflare Access による保護

無料のCloudflare Accessを使用して認証を追加:

1. Cloudflareダッシュボードで Zero Trust > Access > Applications に移動
2. "Add an Application" をクリック
3. Self-hosted を選択
4. アプリケーション名とドメインを設定
5. 認証方法を選択（Email OTP、Google、GitHubなど）
6. ポリシーを設定して保存

### 環境変数の設定

`.env` ファイルにトンネル情報を追加:

```env
CLOUDFLARE_TUNNEL_TOKEN=your_tunnel_token_here
PUBLIC_URL=https://bpsr-market.yourdomain.com
```

## Discord Bot との連携

Discord BotからAPIを呼び出す場合:

```python
import requests

API_URL = "https://bpsr-market.yourdomain.com/api/v1"

# 最新の出品を取得
response = requests.get(f"{API_URL}/listings/latest/all")
listings = response.json()

# 損益計算
profit_data = {
    "buy_price": 1000,
    "sell_price": 1500,
    "quantity": 10,
    "fee_rate": 0.05,
    "has_monthly_card": False
}
response = requests.post(f"{API_URL}/calculate-profit", json=profit_data)
result = response.json()

print(f"利益: {result['profit']}円")
```

## 参考リンク

- [Cloudflare Tunnel 公式ドキュメント](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub](https://github.com/cloudflare/cloudflared)
- [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/applications/configure-apps/)
