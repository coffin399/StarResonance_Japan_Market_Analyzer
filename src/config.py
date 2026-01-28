"""
Configuration management
環境変数と設定の管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Database
    database_url: str = "sqlite:///./bpsr_market.db"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    secret_key: str = "change-this-secret-key-in-production"
    
    # Wireshark/TShark
    tshark_path: str = r"C:\Program Files\Wireshark\tshark.exe"
    pcap_directory: str = "./pcaps"
    
    # Game Server
    game_server_ip: Optional[str] = None
    game_server_port: Optional[int] = None
    
    # Cloudflare Tunnel
    cloudflare_tunnel_token: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# グローバル設定インスタンス
settings = Settings()
