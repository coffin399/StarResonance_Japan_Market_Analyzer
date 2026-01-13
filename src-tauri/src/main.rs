// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod packet_capture;
mod packet_parser;
mod database;
mod models;
mod windivert;
mod windivert_loader;

use std::sync::Arc;
use tokio::sync::Mutex;
use tauri::State;
use tracing::{info, error};

// アプリケーション状態
struct AppState {
    db: Arc<Mutex<database::Database>>,
    capture: Arc<Mutex<Option<packet_capture::PacketCapture>>>,
}

#[tauri::command]
async fn start_packet_capture(state: State<'_, AppState>) -> Result<(), String> {
    info!("パケットキャプチャを開始します");
    
    let mut capture_lock = state.capture.lock().await;
    
    if capture_lock.is_some() {
        return Err("パケットキャプチャは既に実行中です".to_string());
    }

    match packet_capture::PacketCapture::new() {
        Ok(capture) => {
            let db = Arc::clone(&state.db);
            
            // パケットキャプチャを別スレッドで開始
            tokio::spawn(async move {
                if let Err(e) = capture.start(db).await {
                    error!("パケットキャプチャエラー: {}", e);
                }
            });
            
            *capture_lock = Some(capture);
            info!("パケットキャプチャが正常に開始されました");
            Ok(())
        }
        Err(e) => {
            error!("パケットキャプチャの開始に失敗: {}", e);
            Err(format!("パケットキャプチャの開始に失敗しました: {}", e))
        }
    }
}

#[tauri::command]
async fn stop_packet_capture(state: State<'_, AppState>) -> Result<(), String> {
    info!("パケットキャプチャを停止します");
    
    let mut capture_lock = state.capture.lock().await;
    
    if let Some(capture) = capture_lock.take() {
        capture.stop().await.map_err(|e| e.to_string())?;
        info!("パケットキャプチャが正常に停止されました");
        Ok(())
    } else {
        Err("パケットキャプチャは実行されていません".to_string())
    }
}

#[tauri::command]
async fn get_market_data(state: State<'_, AppState>) -> Result<Vec<models::MarketItem>, String> {
    let db = state.db.lock().await;
    db.get_recent_market_data(100)
        .map_err(|e| format!("データベースエラー: {}", e))
}

#[tauri::command]
async fn get_item_history(
    state: State<'_, AppState>,
    item_id: String,
) -> Result<Vec<models::PriceHistory>, String> {
    let db = state.db.lock().await;
    db.get_item_price_history(&item_id, 100)
        .map_err(|e| format!("データベースエラー: {}", e))
}

#[tauri::command]
async fn clear_database(state: State<'_, AppState>) -> Result<(), String> {
    let db = state.db.lock().await;
    db.clear_all_data()
        .map_err(|e| format!("データベースのクリアに失敗: {}", e))
}

fn main() {
    // ロギング設定
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    info!("StarResonance Market Analyzer を起動しています...");

    // データベース初期化
    let db = match database::Database::new() {
        Ok(db) => {
            info!("データベースが正常に初期化されました");
            Arc::new(Mutex::new(db))
        }
        Err(e) => {
            error!("データベースの初期化に失敗: {}", e);
            panic!("データベースの初期化に失敗しました: {}", e);
        }
    };

    let app_state = AppState {
        db,
        capture: Arc::new(Mutex::new(None)),
    };

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            start_packet_capture,
            stop_packet_capture,
            get_market_data,
            get_item_history,
            clear_database,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
