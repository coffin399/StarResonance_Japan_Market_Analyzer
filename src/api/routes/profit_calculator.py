"""
Profit Calculator API routes
損益計算関連のAPIルート
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from ...database import get_db
from ...database.models import Listing, Item
from ..schemas import ProfitCalculationResponse

router = APIRouter()


class ProfitCalculationRequest(BaseModel):
    """損益計算リクエスト"""
    item_id: Optional[int] = Field(None, description="アイテムID")
    buy_price: int = Field(..., gt=0, description="購入価格")
    sell_price: int = Field(..., gt=0, description="販売価格")
    quantity: int = Field(1, gt=0, description="数量")
    fee_rate: float = Field(0.05, ge=0, le=1, description="手数料率（デフォルト5%）")
    has_monthly_card: bool = Field(False, description="マンスリーカード所持")


class BulkProfitCalculationRequest(BaseModel):
    """一括損益計算リクエスト"""
    item_id: int = Field(..., description="アイテムID")
    quantity: int = Field(1, gt=0, description="数量")
    target_profit_rate: float = Field(0.2, ge=0, description="目標利益率（デフォルト20%）")


@router.post("/calculate-profit", response_model=ProfitCalculationResponse)
async def calculate_profit(
    request: ProfitCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    取引の損益を計算
    
    - **item_id**: アイテムID（オプション）
    - **buy_price**: 購入価格
    - **sell_price**: 販売価格
    - **quantity**: 数量
    - **fee_rate**: 手数料率
    - **has_monthly_card**: マンスリーカード所持
    """
    # マンスリーカードで手数料-20%
    effective_fee_rate = request.fee_rate * 0.8 if request.has_monthly_card else request.fee_rate
    
    # 計算
    total_buy_cost = request.buy_price * request.quantity
    total_sell_revenue = request.sell_price * request.quantity
    fee = int(total_sell_revenue * effective_fee_rate)
    net_revenue = total_sell_revenue - fee
    profit = net_revenue - total_buy_cost
    profit_rate = (profit / total_buy_cost * 100) if total_buy_cost > 0 else 0
    roi = (profit / total_buy_cost) if total_buy_cost > 0 else 0
    
    # アイテム情報を取得（指定されている場合）
    item_name = None
    if request.item_id:
        item = db.query(Item).filter(Item.id == request.item_id).first()
        if item:
            item_name = item.name
    
    return {
        "item_id": request.item_id,
        "item_name": item_name,
        "quantity": request.quantity,
        "buy_price": request.buy_price,
        "sell_price": request.sell_price,
        "total_buy_cost": total_buy_cost,
        "total_sell_revenue": total_sell_revenue,
        "fee": fee,
        "fee_rate": effective_fee_rate,
        "net_revenue": net_revenue,
        "profit": profit,
        "profit_rate": profit_rate,
        "roi": roi,
    }


@router.post("/calculate-optimal-price")
async def calculate_optimal_price(
    request: BulkProfitCalculationRequest,
    db: Session = Depends(get_db)
):
    """
    目標利益率を達成するための最適販売価格を計算
    
    - **item_id**: アイテムID
    - **quantity**: 数量
    - **target_profit_rate**: 目標利益率
    """
    # 現在の最安値を取得
    lowest_listing = db.query(Listing).filter(
        Listing.item_id == request.item_id,
        Listing.status == "active"
    ).order_by(Listing.price.asc()).first()
    
    if not lowest_listing:
        raise HTTPException(status_code=404, detail="No active listings found for this item")
    
    # アイテム情報を取得
    item = db.query(Item).filter(Item.id == request.item_id).first()
    
    current_unit_price = lowest_listing.price / lowest_listing.quantity if lowest_listing.quantity > 0 else lowest_listing.price
    buy_price = int(current_unit_price)
    
    # 目標利益を達成するための販売価格を計算
    # profit_rate = (sell_price - buy_price - fee) / buy_price
    # fee = sell_price * 0.05
    # profit_rate = (sell_price - buy_price - sell_price * 0.05) / buy_price
    # profit_rate = (sell_price * 0.95 - buy_price) / buy_price
    # profit_rate * buy_price = sell_price * 0.95 - buy_price
    # sell_price * 0.95 = profit_rate * buy_price + buy_price
    # sell_price = (profit_rate * buy_price + buy_price) / 0.95
    
    fee_rate = 0.05  # デフォルト手数料
    optimal_sell_price = int((request.target_profit_rate * buy_price + buy_price) / (1 - fee_rate))
    
    # 損益計算
    total_buy_cost = buy_price * request.quantity
    total_sell_revenue = optimal_sell_price * request.quantity
    fee = int(total_sell_revenue * fee_rate)
    profit = total_sell_revenue - fee - total_buy_cost
    actual_profit_rate = (profit / total_buy_cost * 100) if total_buy_cost > 0 else 0
    
    return {
        "item_id": request.item_id,
        "item_name": item.name if item else "Unknown",
        "quantity": request.quantity,
        "current_lowest_price": buy_price,
        "target_profit_rate": request.target_profit_rate * 100,
        "optimal_sell_price": optimal_sell_price,
        "expected_profit": profit,
        "actual_profit_rate": actual_profit_rate,
        "total_buy_cost": total_buy_cost,
        "total_revenue": total_sell_revenue,
        "fee": fee,
    }


@router.get("/compare-margins")
async def compare_margins(
    item_id: int,
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    """
    複数の価格帯での利益率を比較
    
    - **item_id**: アイテムID
    - **quantity**: 数量
    """
    # 現在の最安値を取得
    lowest_listing = db.query(Listing).filter(
        Listing.item_id == item_id,
        Listing.status == "active"
    ).order_by(Listing.price.asc()).first()
    
    if not lowest_listing:
        raise HTTPException(status_code=404, detail="No active listings found for this item")
    
    item = db.query(Item).filter(Item.id == item_id).first()
    
    buy_price = int(lowest_listing.price / lowest_listing.quantity if lowest_listing.quantity > 0 else lowest_listing.price)
    
    # 様々な販売価格での利益を計算
    scenarios = []
    for markup in [1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.5, 2.0]:
        sell_price = int(buy_price * markup)
        
        total_buy_cost = buy_price * quantity
        total_sell_revenue = sell_price * quantity
        fee = int(total_sell_revenue * 0.05)
        profit = total_sell_revenue - fee - total_buy_cost
        profit_rate = (profit / total_buy_cost * 100) if total_buy_cost > 0 else 0
        
        scenarios.append({
            "markup": f"{int((markup - 1) * 100)}%",
            "sell_price": sell_price,
            "profit": profit,
            "profit_rate": profit_rate,
        })
    
    return {
        "item_id": item_id,
        "item_name": item.name if item else "Unknown",
        "buy_price": buy_price,
        "quantity": quantity,
        "scenarios": scenarios,
    }
