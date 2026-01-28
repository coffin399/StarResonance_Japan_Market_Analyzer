"""
Trading Center Packet Decoder
取引所パケットのデコーダー

参考: https://github.com/JordieB/bpsr_labs/blob/main/src/bpsr_labs/packet_decoder/decoder/trading_center_decode_v2.py
"""
import struct
from typing import List, Optional
from datetime import datetime
import logging

try:
    from scapy.all import rdpcap, Packet
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from .packet_types import TradingPacket, ItemListing, MarketSnapshot

logger = logging.getLogger(__name__)


class TradingCenterDecoder:
    """取引所パケットのデコーダー"""
    
    # 取引所パケットのマジックバイト
    TRADING_CENTER_MAGIC = bytes([0x00, 0x63, 0x33, 0x53, 0x42, 0x00])
    
    def __init__(self, pcap_file: Optional[str] = None):
        """
        Args:
            pcap_file: Pcapファイルのパス
        """
        self.pcap_file = pcap_file
        self.packets: List[TradingPacket] = []
        
        if not SCAPY_AVAILABLE:
            logger.warning("Scapy is not available. Packet capture functionality is limited.")
    
    def load_pcap(self, pcap_file: str) -> List[Packet]:
        """
        Pcapファイルを読み込む
        
        Args:
            pcap_file: Pcapファイルのパス
            
        Returns:
            パケットのリスト
        """
        if not SCAPY_AVAILABLE:
            raise ImportError("Scapy is required for PCAP file reading")
        
        logger.info(f"Loading PCAP file: {pcap_file}")
        packets = rdpcap(pcap_file)
        logger.info(f"Loaded {len(packets)} packets")
        return packets
    
    def is_trading_packet(self, data: bytes) -> bool:
        """
        取引所パケットかどうかを判定
        
        Args:
            data: パケットデータ
            
        Returns:
            取引所パケットならTrue
        """
        return self.TRADING_CENTER_MAGIC in data
    
    def decode_item_listing(self, data: bytes, offset: int) -> Optional[ItemListing]:
        """
        アイテムリスティング情報をデコード
        
        Args:
            data: パケットデータ
            offset: デコード開始位置
            
        Returns:
            ItemListingオブジェクト
        """
        try:
            # 基本構造の解析（実際のパケット構造に応じて調整が必要）
            # この実装は仮のものです
            
            # リスティングID (8 bytes, little endian)
            if offset + 8 > len(data):
                return None
            listing_id = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
            
            # アイテムID (4 bytes, little endian)
            if offset + 4 > len(data):
                return None
            item_id = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # 数量 (4 bytes, little endian)
            if offset + 4 > len(data):
                return None
            quantity = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # 価格 (8 bytes, little endian)
            if offset + 8 > len(data):
                return None
            price = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
            
            # アイテム名の長さ (2 bytes)
            if offset + 2 > len(data):
                return None
            name_length = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # アイテム名 (UTF-8)
            if offset + name_length > len(data):
                return None
            item_name = data[offset:offset+name_length].decode('utf-8', errors='ignore')
            
            return ItemListing(
                listing_id=str(listing_id),
                item_id=item_id,
                item_name=item_name,
                quantity=quantity,
                price=price,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error decoding item listing: {e}")
            return None
    
    def decode_trading_packet(self, packet_data: bytes) -> TradingPacket:
        """
        取引所パケットをデコード
        
        Args:
            packet_data: パケットデータ
            
        Returns:
            TradingPacketオブジェクト
        """
        trading_packet = TradingPacket(
            packet_type="trading_center",
            raw_data=packet_data,
            timestamp=datetime.now()
        )
        
        # マジックバイトの位置を探す
        magic_pos = packet_data.find(self.TRADING_CENTER_MAGIC)
        if magic_pos == -1:
            logger.warning("Trading center magic bytes not found")
            return trading_packet
        
        # マジックバイトの後からデータを解析
        data_start = magic_pos + len(self.TRADING_CENTER_MAGIC)
        
        # リスティング数を取得（仮定: 4バイト）
        if data_start + 4 <= len(packet_data):
            num_listings = struct.unpack('<I', packet_data[data_start:data_start+4])[0]
            data_start += 4
            
            listings = []
            offset = data_start
            
            # 各リスティングをデコード
            for i in range(min(num_listings, 100)):  # 最大100件まで
                listing = self.decode_item_listing(packet_data, offset)
                if listing:
                    listings.append(listing)
                    # 次のリスティングへ（サイズは推定）
                    offset += 64  # 仮の固定サイズ
                else:
                    break
            
            trading_packet.listings = listings
            trading_packet.decoded_data = {
                "num_listings": len(listings),
                "total_value": sum(l.price * l.quantity for l in listings)
            }
        
        return trading_packet
    
    def decode_pcap_file(self, pcap_file: Optional[str] = None) -> List[TradingPacket]:
        """
        Pcapファイルから取引所パケットをデコード
        
        Args:
            pcap_file: Pcapファイルのパス（省略時はコンストラクタで指定したものを使用）
            
        Returns:
            デコードされたパケットのリスト
        """
        if pcap_file is None:
            pcap_file = self.pcap_file
        
        if pcap_file is None:
            raise ValueError("PCAP file path not specified")
        
        packets = self.load_pcap(pcap_file)
        trading_packets = []
        
        for packet in packets:
            # TCPペイロードを取得
            if packet.haslayer('Raw'):
                payload = bytes(packet['Raw'].load)
                
                if self.is_trading_packet(payload):
                    trading_packet = self.decode_trading_packet(payload)
                    trading_packets.append(trading_packet)
        
        self.packets = trading_packets
        logger.info(f"Decoded {len(trading_packets)} trading packets")
        return trading_packets
    
    def create_market_snapshot(self) -> MarketSnapshot:
        """
        現在のパケットから市場スナップショットを作成
        
        Returns:
            MarketSnapshotオブジェクト
        """
        all_listings = []
        for packet in self.packets:
            if packet.listings:
                all_listings.extend(packet.listings)
        
        return MarketSnapshot(
            timestamp=datetime.now(),
            listings=all_listings,
            total_items=len(all_listings)
        )
    
    def decode_from_bytes(self, data: bytes) -> Optional[TradingPacket]:
        """
        バイト列から直接デコード（リアルタイムキャプチャ用）
        
        Args:
            data: パケットデータ
            
        Returns:
            TradingPacketオブジェクト
        """
        if self.is_trading_packet(data):
            return self.decode_trading_packet(data)
        return None
