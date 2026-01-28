"""
Debug version of packet parser
デバッグ用パケットパーサー - 詳細なログとhexダンプを出力
"""
import sys
import struct
import logging
import warnings
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

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
    level=logging.DEBUG,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def hex_dump(data: bytes, offset: int = 0, length: int = None, width: int = 16) -> str:
    """hexダンプを生成"""
    if length is None:
        length = len(data) - offset
    
    lines = []
    for i in range(0, length, width):
        chunk = data[offset+i:offset+i+width]
        
        # Hex部分
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        hex_part = hex_part.ljust(width * 3)
        
        # ASCII部分
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        
        lines.append(f'{offset+i:08x}: {hex_part} | {ascii_part}')
    
    return '\n'.join(lines)


def find_japanese_strings(data: bytes, min_length: int = 3) -> List[tuple]:
    """日本語文字列とその位置を検索"""
    results = []
    
    i = 0
    while i < len(data) - min_length:
        # 2バイト長さフィールドを探す
        if i + 2 <= len(data):
            try:
                length = struct.unpack('<H', data[i:i+2])[0]
                
                if min_length <= length <= 100:  # 妥当な文字列長
                    start = i + 2
                    end = start + length
                    
                    if end <= len(data):
                        try:
                            text = data[start:end].decode('utf-8', errors='strict')
                            
                            # 日本語文字を含むか（ひらがな、カタカナ、漢字）
                            if any(0x3000 <= ord(c) <= 0x9FFF for c in text):
                                results.append((i, length, text))
                                i = end
                                continue
                        except UnicodeDecodeError:
                            pass
            except:
                pass
        
        i += 1
    
    return results


def extract_numbers_near(data: bytes, pos: int, range_bytes: int = 60) -> List[tuple]:
    """位置の前後から数値を抽出"""
    start = max(0, pos - range_bytes)
    end = min(len(data), pos + range_bytes)
    
    numbers = []
    
    for i in range(start, end - 8):
        # 4バイト整数（リトルエンディアン）
        if i + 4 <= end:
            try:
                num = struct.unpack('<I', data[i:i+4])[0]
                if 1 <= num <= 100000000:  # 妥当な範囲
                    numbers.append(('uint32', i, num))
            except:
                pass
        
        # 8バイト整数（リトルエンディアン）
        if i + 8 <= end:
            try:
                num = struct.unpack('<Q', data[i:i+8])[0]
                if 1 <= num <= 100000000:  # 妥当な範囲
                    numbers.append(('uint64', i, num))
            except:
                pass
    
    return numbers


def analyze_packet(data: bytes, packet_num: int):
    """パケットを詳細に解析"""
    print(f"\n{'='*80}")
    print(f"Packet #{packet_num} - Size: {len(data)} bytes")
    print(f"{'='*80}")
    
    # マジックバイト検索
    magic_bytes = [
        (b'\x00\x63\x33\x53\x42\x00', '00 63 33 53 42 00'),
        (b'\x63\x33\x53\x42', '63 33 53 42'),
        (b'c3SB', 'c3SB (ASCII)'),
    ]
    
    print("\n[1] Magic Bytes Search:")
    found_magic = False
    for magic, name in magic_bytes:
        pos = data.find(magic)
        if pos != -1:
            print(f"  ✓ Found {name} at offset 0x{pos:04x} ({pos})")
            print(f"    Context (32 bytes):")
            print(hex_dump(data, max(0, pos-8), 32))
            found_magic = True
    
    if not found_magic:
        print("  ✗ No magic bytes found")
    
    # 日本語文字列検索
    print("\n[2] Japanese String Search:")
    japanese_strings = find_japanese_strings(data)
    
    if japanese_strings:
        for pos, length, text in japanese_strings:
            print(f"\n  ✓ Found at offset 0x{pos:04x} ({pos}), length {length}:")
            print(f"    Text: {text}")
            print(f"    Hex dump around position:")
            print(hex_dump(data, max(0, pos-16), 64))
            
            # 周辺の数値を探す
            print(f"\n    Numbers nearby (±60 bytes):")
            numbers = extract_numbers_near(data, pos, 60)
            
            # 重複排除して表示
            seen = set()
            for num_type, num_pos, value in numbers:
                if value not in seen:
                    seen.add(value)
                    offset_from_text = num_pos - pos
                    print(f"      {num_type:8s} @ 0x{num_pos:04x} ({offset_from_text:+4d} bytes): {value:,}")
            
            # 推定
            if len(seen) >= 2:
                sorted_nums = sorted(seen)
                print(f"\n    *** Possible interpretation:")
                print(f"        Item name: {text}")
                print(f"        Quantity:  {sorted_nums[0]:,} (smallest number)")
                print(f"        Price:     {sorted_nums[-1]:,} (largest number)")
                if sorted_nums[0] > 0:
                    print(f"        Unit price: {sorted_nums[-1] // sorted_nums[0]:,}")
    else:
        print("  ✗ No Japanese strings found")
    
    # 全体のhexダンプ（最初の256バイト）
    print(f"\n[3] First 256 bytes (hex dump):")
    print(hex_dump(data, 0, min(256, len(data))))


def main():
    if len(sys.argv) < 2:
        print("Usage: python packet_parser_debug.py <pcap_file>")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    
    if not SCAPY_AVAILABLE:
        print("ERROR: scapy is required")
        print("Run: pip install scapy")
        sys.exit(1)
    
    if not Path(pcap_file).exists():
        print(f"ERROR: File not found: {pcap_file}")
        sys.exit(1)
    
    print(f"{'='*80}")
    print(f"DEBUG PACKET PARSER")
    print(f"{'='*80}")
    print(f"File: {pcap_file}")
    
    try:
        packets = rdpcap(pcap_file)
        print(f"Total packets: {len(packets)}")
        
        analyzed = 0
        for i, packet in enumerate(packets):
            if Raw in packet:
                data = bytes(packet[Raw].load)
                
                # 取引所パケットの候補をフィルタ
                if len(data) > 100:  # 最低サイズ
                    # マジックバイトまたは日本語文字列を含む
                    has_magic = any(magic in data for magic, _ in [
                        (b'\x00\x63\x33\x53\x42\x00', ''),
                        (b'\x63\x33\x53\x42', ''),
                        (b'c3SB', '')
                    ])
                    
                    has_japanese = False
                    try:
                        decoded = data.decode('utf-8', errors='ignore')
                        has_japanese = any(0x3000 <= ord(c) <= 0x9FFF for c in decoded)
                    except:
                        pass
                    
                    if has_magic or has_japanese:
                        analyze_packet(data, i + 1)
                        analyzed += 1
                        
                        if analyzed >= 5:  # 最初の5パケットのみ
                            print(f"\n{'='*80}")
                            print(f"Showing first 5 relevant packets. Total found: {analyzed}")
                            print(f"{'='*80}")
                            break
        
        if analyzed == 0:
            print("\n✗ No trading packets found")
            print("\nShowing first 3 packets with Raw data:")
            count = 0
            for i, packet in enumerate(packets):
                if Raw in packet:
                    data = bytes(packet[Raw].load)
                    analyze_packet(data, i + 1)
                    count += 1
                    if count >= 3:
                        break
    
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
