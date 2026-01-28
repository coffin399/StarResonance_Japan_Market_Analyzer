"""
Game Packet Parser V2 - Protobuf Based
ゲームパケットパーサー V2 - Protobuf対応版

Based on: https://github.com/JordieB/bpsr_labs
"""
import sys
import struct
import logging
import warnings
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

# 警告を抑制
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*TripleDES.*')
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
logging.getLogger('scapy').setLevel(logging.ERROR)

try:
    from scapy.all import rdpcap, Raw
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: scapy not available")

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProtobufParser:
    """Protobuf形式のパケットをパース"""
    
    @staticmethod
    def parse_varint(data: bytes, offset: int) -> tuple:
        """Varint (可変長整数) をパース"""
        result = 0
        shift = 0
        pos = offset
        
        while pos < len(data):
            byte = data[pos]
            result |= (byte & 0x7F) << shift
            pos += 1
            
            if not (byte & 0x80):
                break
            
            shift += 7
        
        return result, pos
    
    @staticmethod
    def parse_field(data: bytes, offset: int) -> tuple:
        """Protobufフィールドをパース"""
        if offset >= len(data):
            return None, offset
        
        # フィールドタグ (wire type + field number)
        tag, offset = ProtobufParser.parse_varint(data, offset)
        wire_type = tag & 0x07
        field_number = tag >> 3
        
        value = None
        
        if wire_type == 0:  # Varint
            value, offset = ProtobufParser.parse_varint(data, offset)
        
        elif wire_type == 1:  # 64-bit
            if offset + 8 <= len(data):
                value = struct.unpack('<Q', data[offset:offset+8])[0]
                offset += 8
        
        elif wire_type == 2:  # Length-delimited (文字列やバイト列)
            length, offset = ProtobufParser.parse_varint(data, offset)
            if offset + length <= len(data):
                value = data[offset:offset+length]
                offset += length
        
        elif wire_type == 5:  # 32-bit
            if offset + 4 <= len(data):
                value = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4
        
        return (field_number, wire_type, value), offset


class GamePacketParserV2:
    """ゲームパケットパーサー V2"""
    
    MAGIC_BYTES = bytes([0x00, 0x63, 0x33, 0x53, 0x42, 0x00])
    MAGIC_BYTES_SHORT = b'c3SB'
    
    def __init__(self, pcap_file: str):
        self.pcap_file = Path(pcap_file)
        self.items = []
    
    def parse(self) -> List[Dict]:
        """PCAPファイルをパース"""
        if not SCAPY_AVAILABLE:
            logger.error("scapy is required. Install it with: pip install scapy")
            return []
        
        if not self.pcap_file.exists():
            logger.error(f"File not found: {self.pcap_file}")
            return []
        
        logger.info(f"Parsing {self.pcap_file}")
        
        try:
            packets = rdpcap(str(self.pcap_file))
            logger.info(f"Total packets: {len(packets)}")
            
            for i, packet in enumerate(packets):
                if Raw in packet:
                    data = bytes(packet[Raw].load)
                    
                    # マジックバイトを探す
                    if self.MAGIC_BYTES in data or self.MAGIC_BYTES_SHORT in data:
                        items = self._parse_packet(data)
                        if items:
                            logger.info(f"Packet #{i+1}: Found {len(items)} items")
                            self.items.extend(items)
            
            logger.info(f"Total items extracted: {len(self.items)}")
            return self.items
        
        except Exception as e:
            logger.error(f"Error parsing pcap: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_packet(self, data: bytes) -> List[Dict]:
        """パケットからアイテム情報を抽出"""
        items = []
        
        try:
            # マジックバイトの位置を探す
            magic_pos = data.find(self.MAGIC_BYTES)
            if magic_pos == -1:
                magic_pos = data.find(self.MAGIC_BYTES_SHORT)
                if magic_pos == -1:
                    return items
                offset = magic_pos + len(self.MAGIC_BYTES_SHORT)
            else:
                offset = magic_pos + len(self.MAGIC_BYTES)
            
            # Protobufデータをパース
            parser = ProtobufParser()
            
            while offset < len(data) - 10:
                field, new_offset = parser.parse_field(data, offset)
                
                if field is None or new_offset == offset:
                    break
                
                field_number, wire_type, value = field
                offset = new_offset
                
                # Length-delimited フィールド (アイテムデータの可能性)
                if wire_type == 2 and isinstance(value, bytes) and len(value) > 20:
                    item = self._parse_item_data(value)
                    if item:
                        items.append(item)
        
        except Exception as e:
            logger.debug(f"Error parsing packet: {e}")
        
        return items
    
    def _parse_item_data(self, data: bytes) -> Optional[Dict]:
        """アイテムデータをパース"""
        try:
            parser = ProtobufParser()
            offset = 0
            
            item_data = {
                'listing_id': 0,
                'item_id': 0,
                'item_name': '',
                'quantity': 0,
                'price': 0,
            }
            
            # Protobufフィールドを解析
            while offset < len(data) - 4:
                field, new_offset = parser.parse_field(data, offset)
                
                if field is None or new_offset == offset:
                    break
                
                field_number, wire_type, value = field
                offset = new_offset
                
                # フィールド番号に基づいて値を割り当て
                if wire_type == 0:  # Varint (IDや数量)
                    if 10 <= value <= 999999:  # アイテムIDの範囲
                        if item_data['item_id'] == 0:
                            item_data['item_id'] = value
                    elif 1 <= value <= 9999:  # 数量の範囲
                        if item_data['quantity'] == 0:
                            item_data['quantity'] = value
                    elif value > 1000000:  # 価格やリスティングID
                        if item_data['listing_id'] == 0:
                            item_data['listing_id'] = value
                        elif item_data['price'] == 0:
                            item_data['price'] = value
                
                elif wire_type == 1:  # 64-bit (価格やタイムスタンプ)
                    if 1000 <= value <= 999999999:
                        if item_data['price'] == 0:
                            item_data['price'] = value
                
                elif wire_type == 2:  # Length-delimited (文字列)
                    if isinstance(value, bytes):
                        try:
                            text = value.decode('utf-8', errors='strict')
                            # 日本語文字を含むか
                            if any(0x3000 <= ord(c) <= 0x9FFF for c in text):
                                if not item_data['item_name']:
                                    item_data['item_name'] = text
                        except:
                            pass
            
            # 妥当性チェック
            if (item_data['item_id'] > 0 and 
                item_data['quantity'] > 0 and 
                item_data['price'] > 0):
                
                item_data['unit_price'] = item_data['price'] // item_data['quantity']
                return item_data
        
        except Exception as e:
            logger.debug(f"Error parsing item data: {e}")
        
        return None
    
    def save_results(self, output_file: str = None):
        """結果をJSONファイルに保存"""
        if not self.items:
            logger.warning("No items to save")
            return
        
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'parsed_items_{timestamp}.json'
        
        output_path = Path(output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(self.items)} items to {output_path}")
        return str(output_path)
    
    def print_summary(self):
        """結果のサマリーを表示"""
        if not self.items:
            print("\n✗ No items found")
            return
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: Found {len(self.items)} items")
        print(f"{'='*80}\n")
        
        for i, item in enumerate(self.items[:10], 1):
            print(f"{i}. Item ID: {item['item_id']}")
            if item['item_name']:
                print(f"   Name: {item['item_name']}")
            print(f"   Quantity: {item['quantity']:,}")
            print(f"   Price: {item['price']:,}")
            print(f"   Unit Price: {item['unit_price']:,}")
            print()
        
        if len(self.items) > 10:
            print(f"... and {len(self.items) - 10} more items")


def main():
    if len(sys.argv) < 2:
        print("Usage: python packet_parser_v2.py <pcap_file>")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    
    parser = GamePacketParserV2(pcap_file)
    items = parser.parse()
    
    if items:
        parser.print_summary()
        output_file = parser.save_results()
        print(f"\nResults saved to: {output_file}")
    else:
        print("\n✗ No items extracted")
        print("\nTroubleshooting:")
        print("1. Make sure you captured packets while viewing the trading center")
        print("2. Use Wireshark filter: tcp.port == <game_port>")
        print("3. Try debug parser: python packet_parser_debug.py <pcap_file>")


if __name__ == '__main__':
    main()
