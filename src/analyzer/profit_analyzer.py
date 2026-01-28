"""
Profit Analyzer
利益分析ツール
"""
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ProfitOpportunity:
    """利益機会"""
    item_id: int
    item_name: str
    buy_price: int
    sell_price: int
    quantity: int
    expected_profit: int
    profit_rate: float
    risk_level: str  # "low", "medium", "high"


class ProfitAnalyzer:
    """利益分析クラス"""
    
    def __init__(self, fee_rate: float = 0.05, has_monthly_card: bool = False):
        """
        Args:
            fee_rate: 基本手数料率
            has_monthly_card: マンスリーカード所持
        """
        self.base_fee_rate = fee_rate
        self.has_monthly_card = has_monthly_card
        self.effective_fee_rate = fee_rate * 0.8 if has_monthly_card else fee_rate
    
    def calculate_profit(
        self,
        buy_price: int,
        sell_price: int,
        quantity: int = 1
    ) -> Dict:
        """
        利益を計算
        
        Args:
            buy_price: 購入価格
            sell_price: 販売価格
            quantity: 数量
            
        Returns:
            計算結果の辞書
        """
        total_buy_cost = buy_price * quantity
        total_sell_revenue = sell_price * quantity
        fee = int(total_sell_revenue * self.effective_fee_rate)
        net_revenue = total_sell_revenue - fee
        profit = net_revenue - total_buy_cost
        profit_rate = (profit / total_buy_cost * 100) if total_buy_cost > 0 else 0
        roi = (profit / total_buy_cost) if total_buy_cost > 0 else 0
        
        return {
            "total_buy_cost": total_buy_cost,
            "total_sell_revenue": total_sell_revenue,
            "fee": fee,
            "fee_rate": self.effective_fee_rate,
            "net_revenue": net_revenue,
            "profit": profit,
            "profit_rate": profit_rate,
            "roi": roi,
            "is_profitable": profit > 0,
        }
    
    def calculate_break_even_price(self, buy_price: int) -> int:
        """
        損益分岐点の販売価格を計算
        
        Args:
            buy_price: 購入価格
            
        Returns:
            損益分岐点の販売価格
        """
        # break_even: sell_price * (1 - fee_rate) = buy_price
        # sell_price = buy_price / (1 - fee_rate)
        return int(buy_price / (1 - self.effective_fee_rate))
    
    def calculate_target_sell_price(self, buy_price: int, target_profit_rate: float) -> int:
        """
        目標利益率を達成するための販売価格を計算
        
        Args:
            buy_price: 購入価格
            target_profit_rate: 目標利益率（例: 0.2 = 20%）
            
        Returns:
            必要な販売価格
        """
        # target_profit_rate = (sell_price * (1 - fee_rate) - buy_price) / buy_price
        # target_profit_rate * buy_price = sell_price * (1 - fee_rate) - buy_price
        # sell_price * (1 - fee_rate) = target_profit_rate * buy_price + buy_price
        # sell_price = (target_profit_rate * buy_price + buy_price) / (1 - fee_rate)
        return int((target_profit_rate * buy_price + buy_price) / (1 - self.effective_fee_rate))
    
    def analyze_flip_opportunity(
        self,
        item_id: int,
        item_name: str,
        lowest_buy_price: int,
        average_sell_price: int,
        price_volatility: float,
        quantity: int = 1
    ) -> ProfitOpportunity:
        """
        転売機会を分析
        
        Args:
            item_id: アイテムID
            item_name: アイテム名
            lowest_buy_price: 最安購入価格
            average_sell_price: 平均販売価格
            price_volatility: 価格変動率（標準偏差/平均）
            quantity: 数量
            
        Returns:
            利益機会オブジェクト
        """
        profit_calc = self.calculate_profit(lowest_buy_price, average_sell_price, quantity)
        
        # リスクレベルの判定
        if price_volatility < 0.1:
            risk_level = "low"
        elif price_volatility < 0.3:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return ProfitOpportunity(
            item_id=item_id,
            item_name=item_name,
            buy_price=lowest_buy_price,
            sell_price=average_sell_price,
            quantity=quantity,
            expected_profit=profit_calc["profit"],
            profit_rate=profit_calc["profit_rate"],
            risk_level=risk_level,
        )
    
    def compare_scenarios(
        self,
        buy_price: int,
        markup_rates: List[float] = None
    ) -> List[Dict]:
        """
        複数の販売価格シナリオを比較
        
        Args:
            buy_price: 購入価格
            markup_rates: マークアップ率のリスト
            
        Returns:
            シナリオのリスト
        """
        if markup_rates is None:
            markup_rates = [1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.5, 2.0]
        
        scenarios = []
        for markup in markup_rates:
            sell_price = int(buy_price * markup)
            profit_calc = self.calculate_profit(buy_price, sell_price)
            
            scenarios.append({
                "markup": f"{int((markup - 1) * 100)}%",
                "sell_price": sell_price,
                "profit": profit_calc["profit"],
                "profit_rate": profit_calc["profit_rate"],
                "roi": profit_calc["roi"],
            })
        
        return scenarios
