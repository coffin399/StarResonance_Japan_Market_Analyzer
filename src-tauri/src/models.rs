use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// 取引所のアイテム情報
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MarketItem {
    pub id: String,
    pub name: String,
    pub price: i64,
    pub quantity: i32,
    pub seller_name: Option<String>,
    pub category: Option<String>,
    pub rarity: Option<i32>,
    pub updated_at: DateTime<Utc>,
}

/// 価格履歴
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceHistory {
    pub id: i64,
    pub item_id: String,
    pub price: i64,
    pub quantity: i32,
    pub recorded_at: DateTime<Utc>,
}

/// パケットから抽出された生データ
#[derive(Debug, Clone)]
pub struct RawPacketData {
    pub timestamp: DateTime<Utc>,
    pub source_ip: String,
    pub dest_ip: String,
    pub source_port: u16,
    pub dest_port: u16,
    pub payload: Vec<u8>,
}

/// 取引所パケットの種類
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum MarketPacketType {
    ItemList,          // アイテムリスト取得
    ItemDetail,        // アイテム詳細
    PriceUpdate,       // 価格更新
    TransactionComplete, // 取引完了
    Unknown,
}

/// パースされた取引所パケット
#[derive(Debug, Clone)]
pub struct MarketPacket {
    pub packet_type: MarketPacketType,
    pub items: Vec<MarketItem>,
    pub timestamp: DateTime<Utc>,
}
