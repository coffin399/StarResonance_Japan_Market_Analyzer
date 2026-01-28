"""
Tests for ProfitAnalyzer
"""
import pytest
from src.analyzer import ProfitAnalyzer


class TestProfitAnalyzer:
    """ProfitAnalyzerのテスト"""
    
    def test_calculate_profit_basic(self):
        """基本的な利益計算のテスト"""
        analyzer = ProfitAnalyzer(fee_rate=0.05, has_monthly_card=False)
        result = analyzer.calculate_profit(1000, 1500, 10)
        
        assert result['total_buy_cost'] == 10000
        assert result['total_sell_revenue'] == 15000
        assert result['fee'] == 750  # 15000 * 0.05
        assert result['net_revenue'] == 14250
        assert result['profit'] == 4250
        assert result['profit_rate'] == 42.5
        assert result['is_profitable'] is True
    
    def test_calculate_profit_with_monthly_card(self):
        """マンスリーカード所持時の利益計算テスト"""
        analyzer = ProfitAnalyzer(fee_rate=0.05, has_monthly_card=True)
        result = analyzer.calculate_profit(1000, 1500, 10)
        
        # 手数料は20%減
        expected_fee = int(15000 * 0.05 * 0.8)  # 600
        assert result['fee'] == expected_fee
        assert result['profit'] > 4250  # 手数料が減るので利益増
    
    def test_calculate_profit_loss(self):
        """損失が出る場合のテスト"""
        analyzer = ProfitAnalyzer(fee_rate=0.05)
        result = analyzer.calculate_profit(1000, 1000, 10)
        
        assert result['profit'] < 0  # 手数料分損失
        assert result['is_profitable'] is False
    
    def test_break_even_price(self):
        """損益分岐点の計算テスト"""
        analyzer = ProfitAnalyzer(fee_rate=0.05)
        break_even = analyzer.calculate_break_even_price(1000)
        
        # 損益分岐点で計算すると利益はほぼ0
        result = analyzer.calculate_profit(1000, break_even, 1)
        assert abs(result['profit']) < 5  # 丸め誤差を考慮
    
    def test_target_sell_price(self):
        """目標利益率達成価格の計算テスト"""
        analyzer = ProfitAnalyzer(fee_rate=0.05)
        target_price = analyzer.calculate_target_sell_price(1000, 0.2)
        
        # 計算した価格で売ると約20%の利益が出るはず
        result = analyzer.calculate_profit(1000, target_price, 1)
        assert 19 <= result['profit_rate'] <= 21  # 丸め誤差を考慮
    
    def test_compare_scenarios(self):
        """シナリオ比較のテスト"""
        analyzer = ProfitAnalyzer(fee_rate=0.05)
        scenarios = analyzer.compare_scenarios(1000, [1.1, 1.2, 1.5])
        
        assert len(scenarios) == 3
        assert scenarios[0]['markup'] == "10%"
        assert scenarios[1]['markup'] == "20%"
        assert scenarios[2]['markup'] == "50%"
        
        # マークアップが高いほど利益も高い
        assert scenarios[0]['profit'] < scenarios[1]['profit'] < scenarios[2]['profit']
