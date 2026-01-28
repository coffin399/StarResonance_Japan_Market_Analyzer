"""
Trend Analyzer
トレンド分析ツール
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics


@dataclass
class PriceTrend:
    """価格トレンド"""
    item_id: int
    item_name: str
    current_price: float
    avg_price_7d: float
    avg_price_30d: float
    price_change_7d: float  # パーセント
    price_change_30d: float  # パーセント
    volatility: float
    trend_direction: str  # "up", "down", "stable"


class TrendAnalyzer:
    """トレンド分析クラス"""
    
    @staticmethod
    def calculate_price_trend(price_history: List[Dict]) -> Optional[PriceTrend]:
        """
        価格履歴からトレンドを計算
        
        Args:
            price_history: 価格履歴のリスト（recorded_at, price含む）
            
        Returns:
            PriceTrendオブジェクト
        """
        if not price_history:
            return None
        
        # 日付でソート
        sorted_history = sorted(price_history, key=lambda x: x["recorded_at"])
        
        if len(sorted_history) < 2:
            return None
        
        # 現在価格
        current_price = sorted_history[-1]["price"]
        
        # 7日前と30日前の価格を計算
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        
        prices_7d = [
            h["price"] for h in sorted_history 
            if datetime.fromisoformat(h["recorded_at"].replace("Z", "+00:00")) >= seven_days_ago
        ]
        
        prices_30d = [
            h["price"] for h in sorted_history 
            if datetime.fromisoformat(h["recorded_at"].replace("Z", "+00:00")) >= thirty_days_ago
        ]
        
        if not prices_7d or not prices_30d:
            return None
        
        avg_price_7d = statistics.mean(prices_7d)
        avg_price_30d = statistics.mean(prices_30d)
        
        # 変動率を計算
        price_change_7d = ((current_price - avg_price_7d) / avg_price_7d * 100) if avg_price_7d > 0 else 0
        price_change_30d = ((current_price - avg_price_30d) / avg_price_30d * 100) if avg_price_30d > 0 else 0
        
        # ボラティリティ（標準偏差 / 平均）
        if len(prices_7d) > 1:
            std_dev = statistics.stdev(prices_7d)
            volatility = std_dev / avg_price_7d if avg_price_7d > 0 else 0
        else:
            volatility = 0
        
        # トレンド方向を判定
        if price_change_7d > 5:
            trend_direction = "up"
        elif price_change_7d < -5:
            trend_direction = "down"
        else:
            trend_direction = "stable"
        
        return PriceTrend(
            item_id=sorted_history[0].get("item_id", 0),
            item_name=sorted_history[0].get("item_name", "Unknown"),
            current_price=current_price,
            avg_price_7d=avg_price_7d,
            avg_price_30d=avg_price_30d,
            price_change_7d=price_change_7d,
            price_change_30d=price_change_30d,
            volatility=volatility,
            trend_direction=trend_direction,
        )
    
    @staticmethod
    def detect_price_spike(price_history: List[float], threshold: float = 2.0) -> bool:
        """
        価格の急騰を検出
        
        Args:
            price_history: 価格のリスト
            threshold: 急騰判定の閾値（標準偏差の倍数）
            
        Returns:
            急騰しているかどうか
        """
        if len(price_history) < 3:
            return False
        
        recent_prices = price_history[-10:]  # 最近10件
        older_prices = price_history[:-1]
        
        if len(older_prices) < 2:
            return False
        
        avg_older = statistics.mean(older_prices)
        std_dev = statistics.stdev(older_prices) if len(older_prices) > 1 else 0
        
        latest_price = recent_prices[-1]
        
        # 最新価格が平均 + threshold * 標準偏差を超えている
        return latest_price > (avg_older + threshold * std_dev)
    
    @staticmethod
    def calculate_moving_average(prices: List[float], window: int) -> List[float]:
        """
        移動平均を計算
        
        Args:
            prices: 価格のリスト
            window: 移動平均のウィンドウサイズ
            
        Returns:
            移動平均のリスト
        """
        if len(prices) < window:
            return []
        
        moving_averages = []
        for i in range(len(prices) - window + 1):
            window_prices = prices[i:i + window]
            moving_averages.append(statistics.mean(window_prices))
        
        return moving_averages
    
    @staticmethod
    def identify_support_resistance(prices: List[float], tolerance: float = 0.05) -> Dict:
        """
        サポート・レジスタンスラインを特定
        
        Args:
            prices: 価格のリスト
            tolerance: 価格の許容誤差（5%など）
            
        Returns:
            サポートとレジスタンスの辞書
        """
        if len(prices) < 5:
            return {"support": None, "resistance": None}
        
        # 局所的な最小値・最大値を見つける
        local_mins = []
        local_maxs = []
        
        for i in range(1, len(prices) - 1):
            if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                local_mins.append(prices[i])
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                local_maxs.append(prices[i])
        
        # サポート（最小値の平均）
        support = statistics.mean(local_mins) if local_mins else min(prices)
        
        # レジスタンス（最大値の平均）
        resistance = statistics.mean(local_maxs) if local_maxs else max(prices)
        
        return {
            "support": support,
            "resistance": resistance,
            "current_near_support": abs(prices[-1] - support) / support < tolerance if support > 0 else False,
            "current_near_resistance": abs(prices[-1] - resistance) / resistance < tolerance if resistance > 0 else False,
        }
