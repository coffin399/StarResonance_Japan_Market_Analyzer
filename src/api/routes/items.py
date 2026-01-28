"""
Items API routes
アイテム関連のAPIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ...database import get_db
from ...database.models import Item, Listing, PriceHistory
from ..schemas import ItemResponse, ItemDetailResponse, PriceHistoryResponse

router = APIRouter()


@router.get("/items", response_model=List[ItemResponse])
async def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    アイテム一覧を取得
    
    - **skip**: スキップする件数
    - **limit**: 取得する件数
    - **category**: カテゴリでフィルタ
    - **search**: アイテム名で検索
    """
    query = db.query(Item)
    
    if category:
        query = query.filter(Item.category == category)
    
    if search:
        query = query.filter(Item.name.contains(search))
    
    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/items/{item_id}", response_model=ItemDetailResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    特定のアイテムの詳細情報を取得
    
    - **item_id**: アイテムID
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # 最新の出品情報を取得
    latest_listings = db.query(Listing).filter(
        Listing.item_id == item_id,
        Listing.status == "active"
    ).order_by(Listing.price.asc()).limit(10).all()
    
    # 価格統計を計算
    if latest_listings:
        prices = [listing.price / listing.quantity for listing in latest_listings]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
    else:
        min_price = max_price = avg_price = None
    
    return {
        "id": item.id,
        "name": item.name,
        "name_en": item.name_en,
        "category": item.category,
        "rarity": item.rarity,
        "description": item.description,
        "icon_url": item.icon_url,
        "latest_listings": latest_listings,
        "min_price": min_price,
        "max_price": max_price,
        "avg_price": avg_price,
        "total_listings": len(latest_listings),
    }


@router.get("/items/{item_id}/history", response_model=List[PriceHistoryResponse])
async def get_item_price_history(
    item_id: int,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    アイテムの価格履歴を取得
    
    - **item_id**: アイテムID
    - **days**: 取得する日数（デフォルト: 7日）
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    history = db.query(PriceHistory).filter(
        PriceHistory.item_id == item_id,
        PriceHistory.recorded_at >= start_date
    ).order_by(PriceHistory.recorded_at.asc()).all()
    
    if not history:
        # アイテムが存在するか確認
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
    
    return history


@router.get("/items/{item_id}/lowest-price")
async def get_lowest_price(item_id: int, db: Session = Depends(get_db)):
    """
    アイテムの最安値を取得
    
    - **item_id**: アイテムID
    """
    listing = db.query(Listing).filter(
        Listing.item_id == item_id,
        Listing.status == "active"
    ).order_by(Listing.price.asc()).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="No active listings found")
    
    return {
        "item_id": item_id,
        "lowest_price": listing.price,
        "quantity": listing.quantity,
        "unit_price": listing.price / listing.quantity if listing.quantity > 0 else listing.price,
        "seller": listing.seller_name,
        "captured_at": listing.captured_at,
    }
