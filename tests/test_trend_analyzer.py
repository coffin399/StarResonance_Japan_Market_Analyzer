"""
Tests for TrendAnalyzer
"""
import pytest
from datetime import datetime, timedelta
from src.analyzer import TrendAnalyzer


class TestTrendAnalyzer:
    """TrendAnalyzerのテスト"""
    
    def create_price_history(self, prices, start_date=None):
        """テスト用の価格履歴を作成"""
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=len(prices))
        
        history = []
        for i, price in enumerate(prices):
            date = start_date + timedelta(days=i)
            history.append({
                "item_id": 1,
                "item_name": "Test Item",
                "price": price,
                "recorded_at": date.isoformat()
            })
        return history
    
    def test_calculate_price_trend_upward(self):
        """上昇トレンドの検出テスト"""
        prices = [1000, 1050, 1100, 1150, 1200, 1300, 1400]
        history = self.create_price_history(prices)
        
        trend = TrendAnalyzer.calculate_price_trend(history)
        
        assert trend is not None
        assert trend.trend_direction == "up"
        assert trend.current_price == 1400
        assert trend.price_change_7d > 0
    
    def test_calculate_price_trend_downward(self):
        """下降トレンドの検出テスト"""
        prices = [1400, 1300, 1200, 1100, 1050, 1000, 950]
        history = self.create_price_history(prices)
        
        trend = TrendAnalyzer.calculate_price_trend(history)
        
        assert trend is not None
        assert trend.trend_direction == "down"
        assert trend.price_change_7d < 0
    
    def test_calculate_price_trend_stable(self):
        """安定トレンドの検出テスト"""
        prices = [1000, 1010, 995, 1005, 1000, 1015, 990]
        history = self.create_price_history(prices)
        
        trend = TrendAnalyzer.calculate_price_trend(history)
        
        assert trend is not None
        assert trend.trend_direction == "stable"
        assert abs(trend.price_change_7d) < 5
    
    def test_detect_price_spike(self):
        """価格急騰の検出テスト"""
        # 通常価格の後に急騰
        prices = [1000, 1010, 995, 1005, 1000, 1015, 2000]
        
        assert TrendAnalyzer.detect_price_spike(prices, threshold=2.0) is True
    
    def test_detect_no_price_spike(self):
        """価格急騰なしの検出テスト"""
        prices = [1000, 1010, 995, 1005, 1000, 1015, 1020]
        
        assert TrendAnalyzer.detect_price_spike(prices, threshold=2.0) is False
    
    def test_calculate_moving_average(self):
        """移動平均の計算テスト"""
        prices = [100, 110, 120, 130, 140]
        ma = TrendAnalyzer.calculate_moving_average(prices, window=3)
        
        # 3日移動平均
        assert len(ma) == 3
        assert ma[0] == pytest.approx((100 + 110 + 120) / 3)
        assert ma[1] == pytest.approx((110 + 120 + 130) / 3)
        assert ma[2] == pytest.approx((120 + 130 + 140) / 3)
    
    def test_identify_support_resistance(self):
        """サポート・レジスタンスの特定テスト"""
        # 価格が900-1100の範囲で変動
        prices = [1000, 900, 1100, 950, 1050, 920, 1080, 940, 1070]
        result = TrendAnalyzer.identify_support_resistance(prices)
        
        assert result['support'] is not None
        assert result['resistance'] is not None
        assert result['support'] < result['resistance']
        # サポートは900前後、レジスタンスは1100前後
        assert 850 < result['support'] < 1000
        assert 1000 < result['resistance'] < 1150
