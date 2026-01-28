"""
Listings API routes
出品情報関連のAPIルート
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta

from ...database import get_db
from ...database.models import Listing, Item
from ..schemas import ListingResponse, ListingDetailResponse

router = APIRouter()


@router.get("/listings", response_model=List[ListingResponse])
async def get_listings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    item_id: Optional[int] = None,
    status: str = Query("active"),
    sort_by: str = Query("price", regex="^(price|captured_at)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    出品情報一覧を取得
    
    - **skip**: スキップする件数
    - **limit**: 取得する件数
    - **item_id**: アイテムIDでフィルタ
    - **status**: ステータスでフィルタ (active, sold, expired)
    - **sort_by**: ソートフィールド (price, captured_at)
    - **order**: ソート順 (asc, desc)
    """
    query = db.query(Listing)
    
    if item_id:
        query = query.filter(Listing.item_id == item_id)
    
    if status:
        query = query.filter(Listing.status == status)
    
    # ソート
    if sort_by == "price":
        sort_field = Listing.price
    else:
        sort_field = Listing.captured_at
    
    if order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(sort_field)
    
    listings = query.offset(skip).limit(limit).all()
    return listings


@router.get("/listings/{listing_id}", response_model=ListingDetailResponse)
async def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """
    特定の出品情報を取得
    
    - **listing_id**: リスティングID
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    # アイテム情報を結合
    item = db.query(Item).filter(Item.id == listing.item_id).first()
    
    return {
        "id": listing.id,
        "item_id": listing.item_id,
        "item_name": item.name if item else "Unknown",
        "quantity": listing.quantity,
        "price": listing.price,
        "unit_price": listing.unit_price or (listing.price / listing.quantity if listing.quantity > 0 else listing.price),
        "seller_id": listing.seller_id,
        "seller_name": listing.seller_name,
        "status": listing.status,
        "captured_at": listing.captured_at,
        "expires_at": listing.expires_at,
    }


@router.get("/listings/latest/all")
async def get_latest_listings(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    最新の出品情報を取得
    
    - **limit**: 取得する件数
    """
    listings = db.query(Listing).filter(
        Listing.status == "active"
    ).order_by(desc(Listing.captured_at)).limit(limit).all()
    
    # アイテム情報を含める
    result = []
    for listing in listings:
        item = db.query(Item).filter(Item.id == listing.item_id).first()
        result.append({
            "listing_id": listing.id,
            "item_id": listing.item_id,
            "item_name": item.name if item else "Unknown",
            "quantity": listing.quantity,
            "price": listing.price,
            "unit_price": listing.unit_price or (listing.price / listing.quantity if listing.quantity > 0 else listing.price),
            "seller": listing.seller_name,
            "captured_at": listing.captured_at,
        })
    
    return result


@router.get("/listings/trending")
async def get_trending_items(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    トレンドアイテム（最近活発に取引されているアイテム）を取得
    
    - **hours**: 集計期間（時間）
    - **limit**: 取得する件数
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    # アイテムごとの出品数を集計
    trending = db.query(
        Listing.item_id,
        func.count(Listing.id).label("listing_count"),
        func.min(Listing.price).label("min_price"),
        func.max(Listing.price).label("max_price"),
        func.avg(Listing.price).label("avg_price"),
    ).filter(
        Listing.captured_at >= start_time
    ).group_by(
        Listing.item_id
    ).order_by(
        desc("listing_count")
    ).limit(limit).all()
    
    # アイテム情報を追加
    result = []
    for trend in trending:
        item = db.query(Item).filter(Item.id == trend.item_id).first()
        result.append({
            "item_id": trend.item_id,
            "item_name": item.name if item else "Unknown",
            "listing_count": trend.listing_count,
            "min_price": trend.min_price,
            "max_price": trend.max_price,
            "avg_price": trend.avg_price,
        })
    
    return result
