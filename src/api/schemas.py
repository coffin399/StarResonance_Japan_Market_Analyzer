"""
Pydantic schemas for API
API用のPydanticスキーマ
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Item schemas
class ItemResponse(BaseModel):
    """アイテムレスポンス"""
    id: int
    name: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    rarity: Optional[str] = None
    icon_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class ListingResponse(BaseModel):
    """出品情報レスポンス"""
    id: int
    item_id: int
    quantity: int
    price: int
    unit_price: Optional[int] = None
    seller_name: Optional[str] = None
    status: str
    captured_at: datetime
    
    class Config:
        from_attributes = True


class ItemDetailResponse(BaseModel):
    """アイテム詳細レスポンス"""
    id: int
    name: str
    name_en: Optional[str] = None
    category: Optional[str] = None
    rarity: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    latest_listings: List[ListingResponse] = []
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None
    total_listings: int = 0


class ListingDetailResponse(BaseModel):
    """出品詳細レスポンス"""
    id: int
    item_id: int
    item_name: str
    quantity: int
    price: int
    unit_price: int
    seller_id: Optional[str] = None
    seller_name: Optional[str] = None
    status: str
    captured_at: datetime
    expires_at: Optional[datetime] = None


class PriceHistoryResponse(BaseModel):
    """価格履歴レスポンス"""
    id: int
    item_id: int
    price: int
    quantity: int
    unit_price: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    avg_price: Optional[float] = None
    total_listings: Optional[int] = None
    recorded_at: datetime
    
    class Config:
        from_attributes = True


class MarketStatsResponse(BaseModel):
    """市場統計レスポンス"""
    id: int
    date: datetime
    total_listings: Optional[int] = None
    total_volume: Optional[int] = None
    unique_items: Optional[int] = None
    active_sellers: Optional[int] = None
    
    class Config:
        from_attributes = True


class ProfitCalculationResponse(BaseModel):
    """損益計算レスポンス"""
    item_id: Optional[int] = None
    item_name: Optional[str] = None
    quantity: int
    buy_price: int
    sell_price: int
    total_buy_cost: int
    total_sell_revenue: int
    fee: int
    fee_rate: float
    net_revenue: int
    profit: int
    profit_rate: float
    roi: float
