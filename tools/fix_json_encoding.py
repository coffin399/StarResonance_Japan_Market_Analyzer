"""
Fix JSON file encoding issues
JSONファイルのエンコーディング問題を修正
"""
import sys
import json
from pathlib import Path

def detect_and_fix_encoding(input_file: str):
    """ファイルのエンコーディングを検出して修正"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        return False
    
    # 複数のエンコーディングを試す
    encodings = ['utf-8', 'utf-8-sig', 'cp932', 'shift-jis', 'latin-1', 'iso-8859-1']
    
    data = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            print(f"Trying encoding: {encoding}...", end=' ')
            with open(input_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            print(f"✓ Success!")
            used_encoding = encoding
            break
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            print(f"✗ Failed: {type(e).__name__}")
            continue
    
    if data is None:
        print(f"\n✗ Could not decode file with any supported encoding")
        return False
    
    # UTF-8で再保存
    output_file = input_path.stem + '_fixed' + input_path.suffix
    output_path = input_path.parent / output_file
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✓ File fixed successfully!")
    print(f"{'='*80}")
    print(f"Original encoding: {used_encoding}")
    print(f"Input:  {input_file}")
    print(f"Output: {output_path}")
    print(f"Items:  {len(data)}")
    print(f"\nYou can now use the fixed file:")
    print(f"  tools\\enrich-items.bat {output_path}")
    
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_json_encoding.py <input_file.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    detect_and_fix_encoding(input_file)

if __name__ == '__main__':
    main()
