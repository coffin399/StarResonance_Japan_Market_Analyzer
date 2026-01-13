use crate::models::{MarketItem, PriceHistory};
use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use rusqlite::{params, Connection};
use std::path::PathBuf;
use tracing::info;

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn new() -> Result<Self> {
        let db_path = Self::get_db_path()?;
        info!("データベースパス: {:?}", db_path);

        let conn = Connection::open(&db_path)
            .context("データベース接続に失敗しました")?;

        let db = Database { conn };
        db.init_schema()?;

        Ok(db)
    }

    fn get_db_path() -> Result<PathBuf> {
        let mut path = dirs::data_local_dir()
            .context("ローカルデータディレクトリの取得に失敗")?;
        path.push("StarResonance_Market_Analyzer");
        std::fs::create_dir_all(&path)?;
        path.push("market_data.db");
        Ok(path)
    }

    fn init_schema(&self) -> Result<()> {
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS market_items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                seller_name TEXT,
                category TEXT,
                rarity INTEGER,
                updated_at TEXT NOT NULL
            )",
            [],
        )?;

        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL,
                price INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (item_id) REFERENCES market_items(id)
            )",
            [],
        )?;

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_item_id ON price_history(item_id)",
            [],
        )?;

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_recorded_at ON price_history(recorded_at)",
            [],
        )?;

        info!("データベーススキーマが初期化されました");
        Ok(())
    }

    pub fn insert_market_item(&self, item: &MarketItem) -> Result<()> {
        self.conn.execute(
            "INSERT OR REPLACE INTO market_items 
             (id, name, price, quantity, seller_name, category, rarity, updated_at)
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)",
            params![
                &item.id,
                &item.name,
                item.price,
                item.quantity,
                &item.seller_name,
                &item.category,
                item.rarity,
                item.updated_at.to_rfc3339(),
            ],
        )?;

        // 価格履歴にも記録
        self.conn.execute(
            "INSERT INTO price_history (item_id, price, quantity, recorded_at)
             VALUES (?1, ?2, ?3, ?4)",
            params![
                &item.id,
                item.price,
                item.quantity,
                item.updated_at.to_rfc3339(),
            ],
        )?;

        Ok(())
    }

    pub fn get_recent_market_data(&self, limit: usize) -> Result<Vec<MarketItem>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, name, price, quantity, seller_name, category, rarity, updated_at
             FROM market_items
             ORDER BY updated_at DESC
             LIMIT ?1",
        )?;

        let items = stmt
            .query_map(params![limit], |row| {
                Ok(MarketItem {
                    id: row.get(0)?,
                    name: row.get(1)?,
                    price: row.get(2)?,
                    quantity: row.get(3)?,
                    seller_name: row.get(4)?,
                    category: row.get(5)?,
                    rarity: row.get(6)?,
                    updated_at: row
                        .get::<_, String>(7)?
                        .parse::<DateTime<Utc>>()
                        .unwrap_or_else(|_| Utc::now()),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(items)
    }

    pub fn get_item_price_history(
        &self,
        item_id: &str,
        limit: usize,
    ) -> Result<Vec<PriceHistory>> {
        let mut stmt = self.conn.prepare(
            "SELECT id, item_id, price, quantity, recorded_at
             FROM price_history
             WHERE item_id = ?1
             ORDER BY recorded_at DESC
             LIMIT ?2",
        )?;

        let history = stmt
            .query_map(params![item_id, limit], |row| {
                Ok(PriceHistory {
                    id: row.get(0)?,
                    item_id: row.get(1)?,
                    price: row.get(2)?,
                    quantity: row.get(3)?,
                    recorded_at: row
                        .get::<_, String>(4)?
                        .parse::<DateTime<Utc>>()
                        .unwrap_or_else(|_| Utc::now()),
                })
            })?
            .collect::<Result<Vec<_>, _>>()?;

        Ok(history)
    }

    pub fn clear_all_data(&self) -> Result<()> {
        self.conn.execute("DELETE FROM price_history", [])?;
        self.conn.execute("DELETE FROM market_items", [])?;
        info!("すべてのデータがクリアされました");
        Ok(())
    }

    pub fn get_statistics(&self) -> Result<DatabaseStats> {
        let total_items: i64 = self
            .conn
            .query_row("SELECT COUNT(*) FROM market_items", [], |row| row.get(0))?;

        let total_records: i64 = self
            .conn
            .query_row("SELECT COUNT(*) FROM price_history", [], |row| row.get(0))?;

        Ok(DatabaseStats {
            total_items: total_items as usize,
            total_records: total_records as usize,
        })
    }
}

#[derive(Debug)]
pub struct DatabaseStats {
    pub total_items: usize,
    pub total_records: usize,
}
