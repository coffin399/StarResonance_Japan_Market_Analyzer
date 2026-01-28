"""
Real-time Packet Capture
リアルタイムパケットキャプチャ

WinDivertを使用してリアルタイムでゲームパケットをキャプチャ
参考: https://github.com/winjwinj/bpsr-logs
"""
import logging
import threading
import time
import warnings
from typing import Optional, Callable, List
from datetime import datetime
from queue import Queue

# 警告を抑制
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*TripleDES.*')
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
logging.getLogger('scapy').setLevel(logging.ERROR)

try:
    from scapy.all import sniff, Packet, Raw
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from .decoder import TradingCenterDecoder
from .packet_types import TradingPacket, ItemListing
from ..config import settings

logger = logging.getLogger(__name__)


class RealtimeCaptureCallback:
    """リアルタイムキャプチャのコールバックインターフェース"""
    
    def on_packet_captured(self, packet: TradingPacket):
        """パケットがキャプチャされた時に呼ばれる"""
        pass
    
    def on_listing_found(self, listings: List[ItemListing]):
        """新しい出品情報が見つかった時に呼ばれる"""
        pass
    
    def on_error(self, error: Exception):
        """エラーが発生した時に呼ばれる"""
        pass


class RealtimePacketCapture:
    """
    リアルタイムパケットキャプチャ
    
    WinDivertまたはScapyを使用してゲームトラフィックを監視し、
    取引所パケットをリアルタイムで検出・デコードします。
    """
    
    def __init__(
        self,
        callback: Optional[RealtimeCaptureCallback] = None,
        interface: Optional[str] = None,
        game_server_ip: Optional[str] = None,
        game_server_port: Optional[int] = None
    ):
        """
        Args:
            callback: パケット検出時のコールバック
            interface: ネットワークインターフェース名
            game_server_ip: ゲームサーバーのIPアドレス
            game_server_port: ゲームサーバーのポート
        """
        self.callback = callback or RealtimeCaptureCallback()
        self.interface = interface
        self.game_server_ip = game_server_ip or settings.game_server_ip
        self.game_server_port = game_server_port or settings.game_server_port
        
        self.decoder = TradingCenterDecoder()
        self.is_running = False
        self.capture_thread: Optional[threading.Thread] = None
        self.packet_queue = Queue(maxsize=1000)
        
        self.stats = {
            "total_packets": 0,
            "trading_packets": 0,
            "listings_found": 0,
            "errors": 0,
            "start_time": None,
        }
    
    def start(self):
        """キャプチャを開始"""
        if self.is_running:
            logger.warning("Capture is already running")
            return
        
        if not SCAPY_AVAILABLE:
            error = ImportError("Scapy is not available. Install with: pip install scapy")
            logger.error(str(error))
            self.callback.on_error(error)
            return
        
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        
        # パケットキャプチャスレッド
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        # パケット処理スレッド
        self.process_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.process_thread.start()
        
        logger.info("Real-time packet capture started")
    
    def stop(self):
        """キャプチャを停止"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        
        if self.process_thread:
            self.process_thread.join(timeout=5)
        
        logger.info("Real-time packet capture stopped")
        self._log_stats()
    
    def _capture_loop(self):
        """パケットキャプチャループ"""
        try:
            # フィルタを構築
            capture_filter = self._build_capture_filter()
            
            logger.info(f"Starting packet capture with filter: {capture_filter}")
            
            # Scapyでパケットをキャプチャ
            sniff(
                iface=self.interface,
                filter=capture_filter,
                prn=self._packet_handler,
                store=False,
                stop_filter=lambda p: not self.is_running
            )
            
        except Exception as e:
            logger.error(f"Capture loop error: {e}")
            self.stats["errors"] += 1
            self.callback.on_error(e)
            self.is_running = False
    
    def _process_loop(self):
        """パケット処理ループ"""
        while self.is_running:
            try:
                if not self.packet_queue.empty():
                    packet_data = self.packet_queue.get(timeout=1)
                    self._process_packet(packet_data)
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Process loop error: {e}")
                self.stats["errors"] += 1
    
    def _packet_handler(self, packet: Packet):
        """Scapyパケットハンドラー"""
        try:
            self.stats["total_packets"] += 1
            
            if packet.haslayer(Raw):
                payload = bytes(packet[Raw].load)
                
                # キューに追加（キューが満杯の場合はスキップ）
                if not self.packet_queue.full():
                    self.packet_queue.put(payload)
                else:
                    logger.warning("Packet queue is full, dropping packet")
        
        except Exception as e:
            logger.error(f"Packet handler error: {e}")
            self.stats["errors"] += 1
    
    def _process_packet(self, packet_data: bytes):
        """パケットを処理"""
        try:
            # 取引所パケットかチェック
            if not self.decoder.is_trading_packet(packet_data):
                return
            
            self.stats["trading_packets"] += 1
            
            # デコード
            trading_packet = self.decoder.decode_trading_packet(packet_data)
            
            # コールバック呼び出し
            self.callback.on_packet_captured(trading_packet)
            
            # 出品情報が見つかった場合
            if trading_packet.listings:
                self.stats["listings_found"] += len(trading_packet.listings)
                self.callback.on_listing_found(trading_packet.listings)
                
                logger.info(
                    f"Found {len(trading_packet.listings)} listings in packet"
                )
        
        except Exception as e:
            logger.error(f"Packet processing error: {e}")
            self.stats["errors"] += 1
            self.callback.on_error(e)
    
    def _build_capture_filter(self) -> str:
        """キャプチャフィルタを構築"""
        filters = ["tcp"]
        
        if self.game_server_ip:
            filters.append(f"host {self.game_server_ip}")
        
        if self.game_server_port:
            filters.append(f"port {self.game_server_port}")
        
        return " and ".join(filters)
    
    def _log_stats(self):
        """統計情報をログ出力"""
        if self.stats["start_time"]:
            duration = (datetime.now() - self.stats["start_time"]).total_seconds()
            
            logger.info("=== Capture Statistics ===")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info(f"Total packets: {self.stats['total_packets']}")
            logger.info(f"Trading packets: {self.stats['trading_packets']}")
            logger.info(f"Listings found: {self.stats['listings_found']}")
            logger.info(f"Errors: {self.stats['errors']}")
            
            if duration > 0:
                logger.info(f"Packets/sec: {self.stats['total_packets'] / duration:.2f}")
    
    def get_stats(self) -> dict:
        """統計情報を取得"""
        stats = self.stats.copy()
        
        if stats["start_time"]:
            stats["duration"] = (datetime.now() - stats["start_time"]).total_seconds()
            stats["packets_per_second"] = (
                stats["total_packets"] / stats["duration"]
                if stats["duration"] > 0 else 0
            )
        
        return stats


class DatabaseCallback(RealtimeCaptureCallback):
    """データベースに自動保存するコールバック"""
    
    def __init__(self, db_session):
        """
        Args:
            db_session: SQLAlchemyのセッション
        """
        self.db = db_session
    
    def on_listing_found(self, listings: List[ItemListing]):
        """出品情報をデータベースに保存"""
        from ..database.models import Item, Listing
        
        try:
            for listing_data in listings:
                # アイテムを取得または作成
                item = self.db.query(Item).filter(
                    Item.id == listing_data.item_id
                ).first()
                
                if not item:
                    item = Item(
                        id=listing_data.item_id,
                        name=listing_data.item_name
                    )
                    self.db.add(item)
                
                # リスティングを作成
                listing = Listing(
                    id=int(listing_data.listing_id),
                    item_id=listing_data.item_id,
                    quantity=listing_data.quantity,
                    price=listing_data.price,
                    unit_price=listing_data.price // listing_data.quantity 
                        if listing_data.quantity > 0 else listing_data.price,
                    seller_name=listing_data.seller_name,
                    captured_at=listing_data.timestamp
                )
                self.db.add(listing)
            
            self.db.commit()
            logger.info(f"Saved {len(listings)} listings to database")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database save error: {e}")
    
    def on_error(self, error: Exception):
        """エラーをログ出力"""
        logger.error(f"Capture error: {error}")
