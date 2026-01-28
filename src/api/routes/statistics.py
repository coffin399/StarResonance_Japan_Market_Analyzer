"""
Statistics API routes
統計情報関連のAPIルート
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta

from ...database import get_db
from ...database.models import Listing, Item, Transaction, MarketStatistics
from ..schemas import MarketStatsResponse

router = APIRouter()


@router.get("/statistics/market-overview")
async def get_market_overview(db: Session = Depends(get_db)):
    """
    市場全体の概要を取得
    """
    # アクティブな出品数
    active_listings = db.query(func.count(Listing.id)).filter(
        Listing.status == "active"
    ).scalar()
    
    # ユニークなアイテム数
    unique_items = db.query(func.count(func.distinct(Listing.item_id))).filter(
        Listing.status == "active"
    ).scalar()
    
    # 総出品額
    total_value = db.query(func.sum(Listing.price)).filter(
        Listing.status == "active"
    ).scalar() or 0
    
    # 最近24時間の新規出品数
    last_24h = datetime.utcnow() - timedelta(hours=24)
    new_listings_24h = db.query(func.count(Listing.id)).filter(
        Listing.captured_at >= last_24h
    ).scalar()
    
    return {
        "active_listings": active_listings,
        "unique_items": unique_items,
        "total_value": total_value,
        "new_listings_24h": new_listings_24h,
        "updated_at": datetime.utcnow(),
    }


@router.get("/statistics/daily", response_model=List[MarketStatsResponse])
async def get_daily_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    日次統計を取得
    
    - **days**: 取得する日数
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    stats = db.query(MarketStatistics).filter(
        MarketStatistics.date >= start_date
    ).order_by(MarketStatistics.date.asc()).all()
    
    return stats


@router.get("/statistics/price-distribution")
async def get_price_distribution(
    item_id: int = Query(..., description="アイテムID"),
    db: Session = Depends(get_db)
):
    """
    特定アイテムの価格分布を取得
    
    - **item_id**: アイテムID
    """
    listings = db.query(Listing).filter(
        Listing.item_id == item_id,
        Listing.status == "active"
    ).all()
    
    if not listings:
        return {"item_id": item_id, "distribution": [], "total": 0}
    
    # 価格帯ごとに集計
    prices = [listing.price / listing.quantity if listing.quantity > 0 else listing.price for listing in listings]
    min_price = min(prices)
    max_price = max(prices)
    
    # 10段階に分割
    bins = 10
    price_range = (max_price - min_price) / bins if max_price > min_price else 1
    
    distribution = []
    for i in range(bins):
        lower = min_price + (price_range * i)
        upper = min_price + (price_range * (i + 1))
        count = sum(1 for p in prices if lower <= p < upper or (i == bins - 1 and p == upper))
        distribution.append({
            "range": f"{int(lower)}-{int(upper)}",
            "count": count,
        })
    
    return {
        "item_id": item_id,
        "distribution": distribution,
        "total": len(listings),
        "min_price": min_price,
        "max_price": max_price,
        "avg_price": sum(prices) / len(prices),
    }


@router.get("/statistics/top-sellers")
async def get_top_sellers(
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    トップセラーを取得
    
    - **limit**: 取得する件数
    - **days**: 集計期間（日数）
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    top_sellers = db.query(
        Listing.seller_name,
        func.count(Listing.id).label("listing_count"),
        func.sum(Listing.price).label("total_value"),
    ).filter(
        Listing.captured_at >= start_date,
        Listing.seller_name.isnot(None)
    ).group_by(
        Listing.seller_name
    ).order_by(
        desc("listing_count")
    ).limit(limit).all()
    
    result = []
    for seller in top_sellers:
        result.append({
            "seller_name": seller.seller_name,
            "listing_count": seller.listing_count,
            "total_value": seller.total_value,
        })
    
    return result


@router.get("/statistics/category-breakdown")
async def get_category_breakdown(db: Session = Depends(get_db)):
    """
    カテゴリ別の出品状況を取得
    """
    # アイテムカテゴリごとの集計
    category_stats = db.query(
        Item.category,
        func.count(Listing.id).label("listing_count"),
        func.sum(Listing.price).label("total_value"),
    ).join(
        Listing, Item.id == Listing.item_id
    ).filter(
        Listing.status == "active"
    ).group_by(
        Item.category
    ).all()
    
    result = []
    for stat in category_stats:
        if stat.category:
            result.append({
                "category": stat.category,
                "listing_count": stat.listing_count,
                "total_value": stat.total_value,
            })
    
    return result
