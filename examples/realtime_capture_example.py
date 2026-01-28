"""
Real-time packet capture example
リアルタイムパケットキャプチャの使用例
"""
import sys
sys.path.insert(0, '.')

import time
import signal
import warnings
import logging

# 警告を抑制
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*TripleDES.*')
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
logging.getLogger('scapy').setLevel(logging.ERROR)

from src.packet_decoder.realtime_capture import (
    RealtimePacketCapture,
    RealtimeCaptureCallback,
    DatabaseCallback
)
from src.database import SessionLocal
from src.packet_decoder.packet_types import ItemListing, TradingPacket
from typing import List


class ConsoleCallback(RealtimeCaptureCallback):
    """コンソールに出力するコールバック"""
    
    def on_packet_captured(self, packet: TradingPacket):
        """パケットがキャプチャされた"""
        print(f"[PACKET] Captured trading packet at {packet.timestamp}")
    
    def on_listing_found(self, listings: List[ItemListing]):
        """新しい出品情報が見つかった"""
        print(f"\n[NEW LISTINGS] Found {len(listings)} new listings:")
        for listing in listings:
            print(f"  - {listing.item_name} x{listing.quantity} @ {listing.price:,}円")
            if listing.seller_name:
                print(f"    Seller: {listing.seller_name}")
    
    def on_error(self, error: Exception):
        """エラーが発生した"""
        print(f"[ERROR] {error}")


def example_basic_capture():
    """基本的なリアルタイムキャプチャ"""
    print("=== Basic Real-time Capture Example ===\n")
    print("Starting packet capture...")
    print("Open the game and access the trading center.")
    print("Press Ctrl+C to stop.\n")
    
    # コールバックを作成
    callback = ConsoleCallback()
    
    # キャプチャを開始
    capture = RealtimePacketCapture(callback=callback)
    
    # Ctrl+Cで停止できるようにする
    def signal_handler(sig, frame):
        print("\n\nStopping capture...")
        capture.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        capture.start()
        
        # 統計情報を定期的に表示
        while True:
            time.sleep(10)
            stats = capture.get_stats()
            print(f"\n[STATS] Total: {stats['total_packets']}, "
                  f"Trading: {stats['trading_packets']}, "
                  f"Listings: {stats['listings_found']}")
    
    except KeyboardInterrupt:
        print("\nStopping...")
        capture.stop()


def example_database_capture():
    """データベースに自動保存するキャプチャ"""
    print("=== Database Auto-save Capture Example ===\n")
    print("Starting packet capture with database auto-save...")
    print("Data will be saved to database automatically.")
    print("Press Ctrl+C to stop.\n")
    
    # データベースセッション
    db = SessionLocal()
    
    # コールバックを組み合わせる
    console_callback = ConsoleCallback()
    db_callback = DatabaseCallback(db)
    
    # 複合コールバック
    class CombinedCallback(RealtimeCaptureCallback):
        def on_packet_captured(self, packet: TradingPacket):
            console_callback.on_packet_captured(packet)
        
        def on_listing_found(self, listings: List[ItemListing]):
            console_callback.on_listing_found(listings)
            db_callback.on_listing_found(listings)
        
        def on_error(self, error: Exception):
            console_callback.on_error(error)
            db_callback.on_error(error)
    
    callback = CombinedCallback()
    
    # キャプチャを開始
    capture = RealtimePacketCapture(callback=callback)
    
    def signal_handler(sig, frame):
        print("\n\nStopping capture...")
        capture.stop()
        db.close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        capture.start()
        
        while True:
            time.sleep(10)
            stats = capture.get_stats()
            print(f"\n[STATS] Listings saved to database: {stats['listings_found']}")
    
    except KeyboardInterrupt:
        print("\nStopping...")
        capture.stop()
        db.close()


def example_filtered_capture():
    """特定のゲームサーバーのみをキャプチャ"""
    print("=== Filtered Capture Example ===\n")
    
    # ゲームサーバーのIPとポートを指定
    game_server_ip = input("Enter game server IP (or press Enter to skip): ").strip()
    game_server_port = input("Enter game server port (or press Enter to skip): ").strip()
    
    if game_server_port:
        game_server_port = int(game_server_port)
    else:
        game_server_port = None
    
    if not game_server_ip:
        game_server_ip = None
    
    callback = ConsoleCallback()
    capture = RealtimePacketCapture(
        callback=callback,
        game_server_ip=game_server_ip,
        game_server_port=game_server_port
    )
    
    def signal_handler(sig, frame):
        print("\n\nStopping capture...")
        capture.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"\nCapturing packets from:")
    print(f"  IP: {game_server_ip or 'Any'}")
    print(f"  Port: {game_server_port or 'Any'}")
    print("\nPress Ctrl+C to stop.\n")
    
    try:
        capture.start()
        
        while True:
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nStopping...")
        capture.stop()


if __name__ == "__main__":
    print("Star Resonance Market Analyzer - Real-time Capture Examples\n")
    print("Select an example:")
    print("1. Basic capture (console output only)")
    print("2. Database auto-save capture")
    print("3. Filtered capture (specific server)")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    print()
    
    if choice == "1":
        example_basic_capture()
    elif choice == "2":
        example_database_capture()
    elif choice == "3":
        example_filtered_capture()
    else:
        print("Invalid choice!")
        sys.exit(1)
