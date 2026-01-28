"""
Basic usage example
基本的な使い方の例
"""
import sys
sys.path.insert(0, '.')

from src.packet_decoder import TradingCenterDecoder
from src.analyzer import ProfitAnalyzer, TrendAnalyzer


def example_decode_pcap():
    """Pcapファイルからパケットをデコードする例"""
    print("=== Pcapファイルのデコード ===")
    
    # デコーダーを初期化
    decoder = TradingCenterDecoder("pcaps/trading_capture.pcap")
    
    # パケットをデコード
    packets = decoder.decode_pcap_file()
    
    print(f"デコードしたパケット数: {len(packets)}")
    
    # 市場スナップショットを作成
    snapshot = decoder.create_market_snapshot()
    print(f"出品アイテム数: {snapshot.total_items}")
    
    # 最初の5件を表示
    for listing in snapshot.listings[:5]:
        print(f"  - {listing.item_name}: {listing.quantity}個 @ {listing.price}円")


def example_calculate_profit():
    """損益計算の例"""
    print("\n=== 損益計算 ===")
    
    # 通常の手数料
    analyzer = ProfitAnalyzer(fee_rate=0.05, has_monthly_card=False)
    
    result = analyzer.calculate_profit(
        buy_price=1000,
        sell_price=1500,
        quantity=10
    )
    
    print(f"購入総額: {result['total_buy_cost']}円")
    print(f"販売総額: {result['total_sell_revenue']}円")
    print(f"手数料: {result['fee']}円")
    print(f"純利益: {result['profit']}円")
    print(f"利益率: {result['profit_rate']:.2f}%")
    print(f"ROI: {result['roi']:.2%}")
    
    # 損益分岐点を計算
    break_even = analyzer.calculate_break_even_price(1000)
    print(f"\n損益分岐点: {break_even}円")
    
    # 目標利益率20%を達成する価格
    target_price = analyzer.calculate_target_sell_price(1000, 0.2)
    print(f"20%利益を得るには: {target_price}円で販売")


def example_compare_scenarios():
    """複数シナリオの比較例"""
    print("\n=== シナリオ比較 ===")
    
    analyzer = ProfitAnalyzer(fee_rate=0.05)
    scenarios = analyzer.compare_scenarios(buy_price=1000)
    
    print("購入価格: 1000円")
    print("\nマークアップ | 販売価格 | 利益 | 利益率")
    print("-" * 50)
    
    for scenario in scenarios:
        print(f"{scenario['markup']:>10} | {scenario['sell_price']:>8}円 | "
              f"{scenario['profit']:>6}円 | {scenario['profit_rate']:>5.1f}%")


def example_trend_analysis():
    """トレンド分析の例"""
    print("\n=== トレンド分析 ===")
    
    # サンプル価格履歴
    price_history = [
        {"item_id": 1, "item_name": "サンプルアイテム", "price": 1000, "recorded_at": "2026-01-20T00:00:00"},
        {"item_id": 1, "item_name": "サンプルアイテム", "price": 1050, "recorded_at": "2026-01-21T00:00:00"},
        {"item_id": 1, "item_name": "サンプルアイテム", "price": 1100, "recorded_at": "2026-01-22T00:00:00"},
        {"item_id": 1, "item_name": "サンプルアイテム", "price": 1200, "recorded_at": "2026-01-23T00:00:00"},
        {"item_id": 1, "item_name": "サンプルアイテム", "price": 1250, "recorded_at": "2026-01-28T00:00:00"},
    ]
    
    trend = TrendAnalyzer.calculate_price_trend(price_history)
    
    if trend:
        print(f"アイテム: {trend.item_name}")
        print(f"現在価格: {trend.current_price}円")
        print(f"7日平均: {trend.avg_price_7d:.0f}円")
        print(f"7日変動: {trend.price_change_7d:+.1f}%")
        print(f"トレンド: {trend.trend_direction}")
        print(f"ボラティリティ: {trend.volatility:.2%}")


if __name__ == "__main__":
    print("Star Resonance Market Analyzer - 使用例\n")
    
    # 注意: Pcapファイルがない場合はスキップ
    # example_decode_pcap()
    
    example_calculate_profit()
    example_compare_scenarios()
    example_trend_analysis()
    
    print("\n完了!")
