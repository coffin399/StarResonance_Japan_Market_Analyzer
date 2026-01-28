"""
Packet data structures
パケットのデータ構造定義
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class ItemListing:
    """取引所の出品情報"""
    listing_id: str
    item_id: int
    item_name: str
    quantity: int
    price: int
    seller_id: Optional[str] = None
    seller_name: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "listing_id": self.listing_id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "price": self.price,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class TradingPacket:
    """取引所パケットの情報"""
    packet_type: str  # "listing", "purchase", "search", etc.
    raw_data: bytes
    decoded_data: Optional[dict] = None
    listings: Optional[List[ItemListing]] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class MarketSnapshot:
    """市場のスナップショット"""
    timestamp: datetime
    listings: List[ItemListing]
    total_items: int
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "listings": [listing.to_dict() for listing in self.listings],
            "total_items": self.total_items,
        }
