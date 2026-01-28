"""
Database models
データベースモデル定義
"""
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Index, Text, Float
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Item(Base):
    """アイテム情報テーブル"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, comment="アイテムID")
    name = Column(String(255), nullable=False, comment="アイテム名")
    name_en = Column(String(255), nullable=True, comment="英語名")
    category = Column(String(100), nullable=True, comment="カテゴリ")
    rarity = Column(String(50), nullable=True, comment="レアリティ")
    description = Column(Text, nullable=True, comment="説明")
    icon_url = Column(String(500), nullable=True, comment="アイコンURL")
    created_at = Column(DateTime, default=datetime.utcnow, comment="作成日時")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新日時")
    
    # リレーション
    listings = relationship("Listing", back_populates="item")
    price_history = relationship("PriceHistory", back_populates="item")
    
    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}')>"


class Listing(Base):
    """出品情報テーブル"""
    __tablename__ = "listings"
    
    id = Column(BigInteger, primary_key=True, index=True, comment="リスティングID")
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True, comment="アイテムID")
    quantity = Column(Integer, nullable=False, comment="数量")
    price = Column(BigInteger, nullable=False, comment="価格")
    unit_price = Column(BigInteger, nullable=True, comment="単価")
    seller_id = Column(String(100), nullable=True, comment="出品者ID")
    seller_name = Column(String(255), nullable=True, comment="出品者名")
    status = Column(String(50), default="active", comment="ステータス (active, sold, expired)")
    captured_at = Column(DateTime, default=datetime.utcnow, index=True, comment="キャプチャ日時")
    expires_at = Column(DateTime, nullable=True, comment="期限")
    
    # リレーション
    item = relationship("Item", back_populates="listings")
    
    # インデックス
    __table_args__ = (
        Index("idx_item_status_captured", "item_id", "status", "captured_at"),
        Index("idx_price_captured", "price", "captured_at"),
    )
    
    def __repr__(self):
        return f"<Listing(id={self.id}, item_id={self.item_id}, price={self.price})>"


class PriceHistory(Base):
    """価格履歴テーブル"""
    __tablename__ = "price_history"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True, comment="アイテムID")
    price = Column(BigInteger, nullable=False, comment="価格")
    quantity = Column(Integer, nullable=False, comment="数量")
    unit_price = Column(BigInteger, nullable=True, comment="単価")
    min_price = Column(BigInteger, nullable=True, comment="最安値")
    max_price = Column(BigInteger, nullable=True, comment="最高値")
    avg_price = Column(Float, nullable=True, comment="平均価格")
    total_listings = Column(Integer, nullable=True, comment="出品数")
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True, comment="記録日時")
    
    # リレーション
    item = relationship("Item", back_populates="price_history")
    
    # インデックス
    __table_args__ = (
        Index("idx_item_recorded", "item_id", "recorded_at"),
    )
    
    def __repr__(self):
        return f"<PriceHistory(item_id={self.item_id}, price={self.price}, recorded_at={self.recorded_at})>"


class Transaction(Base):
    """取引履歴テーブル"""
    __tablename__ = "transactions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    listing_id = Column(BigInteger, index=True, comment="リスティングID")
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True, comment="アイテムID")
    quantity = Column(Integer, nullable=False, comment="数量")
    price = Column(BigInteger, nullable=False, comment="価格")
    buyer_id = Column(String(100), nullable=True, comment="購入者ID")
    buyer_name = Column(String(255), nullable=True, comment="購入者名")
    seller_id = Column(String(100), nullable=True, comment="出品者ID")
    seller_name = Column(String(255), nullable=True, comment="出品者名")
    fee = Column(BigInteger, nullable=True, comment="手数料")
    transaction_type = Column(String(50), default="purchase", comment="取引タイプ")
    completed_at = Column(DateTime, default=datetime.utcnow, index=True, comment="取引完了日時")
    
    # インデックス
    __table_args__ = (
        Index("idx_item_completed", "item_id", "completed_at"),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, item_id={self.item_id}, price={self.price})>"


class MarketStatistics(Base):
    """市場統計テーブル"""
    __tablename__ = "market_statistics"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False, index=True, comment="日付")
    total_listings = Column(Integer, nullable=True, comment="総出品数")
    total_volume = Column(BigInteger, nullable=True, comment="総取引額")
    unique_items = Column(Integer, nullable=True, comment="ユニークアイテム数")
    active_sellers = Column(Integer, nullable=True, comment="アクティブな出品者数")
    created_at = Column(DateTime, default=datetime.utcnow, comment="作成日時")
    
    def __repr__(self):
        return f"<MarketStatistics(date={self.date}, total_listings={self.total_listings})>"
