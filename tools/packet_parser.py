"""
Game Packet Parser
ゲームパケット専用パーサー

Wiresharkでキャプチャしたpcapファイルからゲームの取引所データを抽出します。
"""
import sys
import struct
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GamePacketParser:
    """ゲームパケット専用パーサー"""
    
    # 取引所パケットのマジックバイト候補
    MAGIC_BYTES_CANDIDATES = [
        bytes([0x00, 0x63, 0x33, 0x53, 0x42, 0x00]),  # 既知のパターン
        bytes([0x63, 0x33, 0x53, 0x42]),              # 短縮版
        b'c3SB',                                       # ASCII版
    ]
    
    def __init__(self, pcap_file: str):
        """
        Args:
            pcap_file: Pcapファイルのパス
        """
        self.pcap_file = Path(pcap_file)
        self.packets_found = 0
        self.trading_packets = 0
        self.items_found = []
        
        if not self.pcap_file.exists():
            raise FileNotFoundError(f"File not found: {pcap_file}")
    
    def parse(self) -> List[Dict]:
        """
        Pcapファイルを解析
        
        Returns:
            見つかったアイテムのリスト
        """
        logger.info(f"Parsing pcap file: {self.pcap_file}")
        
        try:
            # Scapyを使用してパケットを読み込み
            from scapy.all import rdpcap, TCP, Raw
            
            packets = rdpcap(str(self.pcap_file))
            logger.info(f"Loaded {len(packets)} packets")
            
            self.packets_found = len(packets)
            
            for i, packet in enumerate(packets):
                if packet.haslayer(TCP) and packet.haslayer(Raw):
                    payload = bytes(packet[Raw].load)
                    
                    # パケット情報をログ出力（最初の10件のみ）
                    if i < 10:
                        logger.debug(f"Packet {i}: Size={len(payload)}, Preview={payload[:50].hex()}")
                    
                    # 取引所パケットかチェック
                    if self._is_trading_packet(payload):
                        self.trading_packets += 1
                        items = self._extract_items(payload)
                        if items:
                            self.items_found.extend(items)
                            logger.info(f"Found {len(items)} items in packet {i}")
            
            logger.info(f"Parsing complete: {self.trading_packets} trading packets found")
            logger.info(f"Total items extracted: {len(self.items_found)}")
            
            return self.items_found
        
        except ImportError:
            logger.error("Scapy is not installed. Using raw packet parsing...")
            return self._parse_raw()
        
        except Exception as e:
            logger.error(f"Error parsing pcap: {e}")
            raise
    
    def _is_trading_packet(self, data: bytes) -> bool:
        """取引所パケットかどうかを判定"""
        # 複数のマジックバイトパターンをチェック
        for magic in self.MAGIC_BYTES_CANDIDATES:
            if magic in data:
                return True
        
        # サイズチェック（取引所パケットは通常100バイト以上）
        if len(data) > 100:
            # UTF-8の日本語文字列を探す（アイテム名の可能性）
            try:
                decoded = data.decode('utf-8', errors='ignore')
                if any(ord(c) > 0x3000 for c in decoded):  # 日本語文字を含む
                    return True
            except:
                pass
        
        return False
    
    def _extract_items(self, data: bytes) -> List[Dict]:
        """パケットからアイテム情報を抽出"""
        items = []
        
        try:
            # マジックバイトの位置を探す
            magic_pos = -1
            for magic in self.MAGIC_BYTES_CANDIDATES:
                pos = data.find(magic)
                if pos != -1:
                    magic_pos = pos
                    break
            
            if magic_pos == -1:
                # マジックバイトなしで日本語文字列を探す
                return self._extract_items_by_string(data)
            
            # マジックバイトの後からデータを解析
            offset = magic_pos + 6
            
            # リスティング数を取得（推定）
            if offset + 4 <= len(data):
                try:
                    num_listings = struct.unpack('<I', data[offset:offset+4])[0]
                    if num_listings > 0 and num_listings < 1000:  # 妥当な範囲
                        offset += 4
                        
                        for i in range(min(num_listings, 100)):
                            item = self._parse_item_data(data, offset)
                            if item:
                                items.append(item)
                                offset += 100  # 次のアイテムへ（推定サイズ）
                            else:
                                break
                except:
                    pass
            
            # マジックバイト方式で見つからない場合
            if not items:
                items = self._extract_items_by_string(data)
        
        except Exception as e:
            logger.debug(f"Error extracting items: {e}")
        
        return items
    
    def _parse_item_data(self, data: bytes, offset: int) -> Optional[Dict]:
        """個別のアイテムデータを解析"""
        try:
            if offset + 30 > len(data):
                return None
            
            # リスティングID（8バイト）
            listing_id = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
            
            # アイテムID（4バイト）
            item_id = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # 数量（4バイト）
            quantity = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            
            # 価格（8バイト）
            price = struct.unpack('<Q', data[offset:offset+8])[0]
            offset += 8
            
            # アイテム名の長さ（2バイト）
            if offset + 2 > len(data):
                return None
            name_length = struct.unpack('<H', data[offset:offset+2])[0]
            offset += 2
            
            # アイテム名
            if offset + name_length > len(data) or name_length > 200:
                return None
            
            item_name = data[offset:offset+name_length].decode('utf-8', errors='ignore').strip()
            
            # 妥当性チェック
            if (item_id > 0 and item_id < 1000000 and 
                quantity > 0 and quantity < 10000 and
                price > 0 and price < 1000000000 and
                len(item_name) > 0):
                
                return {
                    "listing_id": listing_id,
                    "item_id": item_id,
                    "item_name": item_name,
                    "quantity": quantity,
                    "price": price,
                    "unit_price": price // quantity if quantity > 0 else price,
                }
        
        except Exception as e:
            logger.debug(f"Error parsing item at offset {offset}: {e}")
        
        return None
    
    def _extract_items_by_string(self, data: bytes) -> List[Dict]:
        """文字列検索でアイテムを抽出（フォールバック方式）"""
        items = []
        
        try:
            # UTF-8文字列を探す
            i = 0
            while i < len(data) - 10:
                # 文字列の長さヒント（2バイト長さフィールドを探す）
                if i + 2 <= len(data):
                    possible_length = struct.unpack('<H', data[i:i+2])[0]
                    
                    if 3 < possible_length < 100:  # 妥当な文字列長
                        start = i + 2
                        end = start + possible_length
                        
                        if end <= len(data):
                            try:
                                text = data[start:end].decode('utf-8', errors='strict')
                                
                                # 日本語文字を含むか
                                if any(ord(c) > 0x3000 for c in text):
                                    # アイテム名候補
                                    logger.info(f"Found possible item name: {text}")
                                    
                                    # 前後のデータから価格と数量を推定
                                    item_data = self._extract_nearby_numbers(data, i)
                                    if item_data:
                                        item_data['item_name'] = text
                                        items.append(item_data)
                                        
                                    i = end
                                    continue
                            except:
                                pass
                
                i += 1
        
        except Exception as e:
            logger.debug(f"Error in string extraction: {e}")
        
        return items
    
    def _extract_nearby_numbers(self, data: bytes, pos: int) -> Optional[Dict]:
        """位置の前後から数値データを抽出"""
        try:
            # 前後40バイトを探索
            search_range = data[max(0, pos-40):min(len(data), pos+40)]
            
            numbers = []
            for i in range(0, len(search_range) - 8, 4):
                try:
                    # 4バイト整数
                    num = struct.unpack('<I', search_range[i:i+4])[0]
                    if 1 < num < 1000000000:
                        numbers.append(num)
                    
                    # 8バイト整数
                    if i + 8 <= len(search_range):
                        num64 = struct.unpack('<Q', search_range[i:i+8])[0]
                        if 1 < num64 < 1000000000:
                            numbers.append(num64)
                except:
                    pass
            
            if len(numbers) >= 2:
                # 小さい数字が数量、大きい数字が価格と推定
                numbers.sort()
                quantity = numbers[0]
                price = numbers[-1]
                
                return {
                    "listing_id": 0,
                    "item_id": 0,
                    "quantity": quantity,
                    "price": price,
                    "unit_price": price // quantity if quantity > 0 else price,
                }
        
        except Exception as e:
            logger.debug(f"Error extracting numbers: {e}")
        
        return None
    
    def _parse_raw(self) -> List[Dict]:
        """Raw バイナリファイルとして解析（Scapyなし）"""
        logger.info("Parsing as raw binary file...")
        items = []
        
        with open(self.pcap_file, 'rb') as f:
            data = f.read()
            
            # 取引所パケットのパターンを探す
            for magic in self.MAGIC_BYTES_CANDIDATES:
                pos = 0
                while True:
                    pos = data.find(magic, pos)
                    if pos == -1:
                        break
                    
                    logger.info(f"Found magic bytes at position {pos}")
                    
                    # この位置からデータを抽出
                    extracted = self._extract_items(data[pos:pos+10000])
                    items.extend(extracted)
                    
                    pos += 1
        
        return items
    
    def save_results(self, output_file: str = None):
        """結果をJSONファイルに保存"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"parsed_items_{timestamp}.json"
        
        result = {
            "pcap_file": str(self.pcap_file),
            "parsed_at": datetime.now().isoformat(),
            "total_packets": self.packets_found,
            "trading_packets": self.trading_packets,
            "items_found": len(self.items_found),
            "items": self.items_found,
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
        return output_file


def main():
    """メイン処理"""
    print("=" * 60)
    print("Game Packet Parser")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python packet_parser.py <pcap_file>")
        print()
        print("Example:")
        print("  python packet_parser.py capture.pcap")
        print()
        return 1
    
    pcap_file = sys.argv[1]
    
    try:
        # パーサーを作成
        parser = GamePacketParser(pcap_file)
        
        # 解析実行
        items = parser.parse()
        
        # 結果を表示
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Total packets: {parser.packets_found}")
        print(f"Trading packets: {parser.trading_packets}")
        print(f"Items found: {len(items)}")
        print()
        
        if items:
            print("Sample items:")
            for item in items[:10]:
                print(f"  - {item.get('item_name', 'Unknown')}: "
                      f"{item['quantity']}x @ {item['price']:,} "
                      f"(unit: {item['unit_price']:,})")
            
            if len(items) > 10:
                print(f"  ... and {len(items) - 10} more items")
            print()
            
            # 結果を保存
            output_file = parser.save_results()
            print(f"Full results saved to: {output_file}")
        else:
            print("No items found. Possible reasons:")
            print("  1. The pcap file doesn't contain trading center packets")
            print("  2. The packet structure is different from expected")
            print("  3. Packets are encrypted or compressed")
            print()
            print("Suggestions:")
            print("  - Capture packets while actively browsing the trading center")
            print("  - Make sure you're capturing the correct network interface")
            print("  - Check if the game server IP/port is correct")
        
        print()
        print("=" * 60)
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Parsing failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
