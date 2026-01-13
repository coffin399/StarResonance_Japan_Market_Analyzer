use crate::database::Database;
use crate::models::RawPacketData;
use crate::packet_parser::PacketParser;
use crate::windivert::{WinDivert, WinDivertAddress, WINDIVERT_FLAG_SNIFF, WINDIVERT_LAYER_NETWORK};
use anyhow::{Context, Result};
use chrono::Utc;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use tokio::sync::Mutex;
use tracing::{error, info, warn, debug};

pub struct PacketCapture {
    running: Arc<AtomicBool>,
}

impl PacketCapture {
    pub fn new() -> Result<Self> {
        info!("PacketCapture を初期化中...");

        Ok(PacketCapture {
            running: Arc::new(AtomicBool::new(false)),
        })
    }

    fn check_admin_privileges() -> Result<()> {
        #[cfg(windows)]
        {
            use std::ptr;
            use windows::Win32::Foundation::BOOL;
            use windows::Win32::Security::{GetTokenInformation, TokenElevation, TOKEN_ELEVATION, TOKEN_QUERY};
            use windows::Win32::System::Threading::{GetCurrentProcess, OpenProcessToken};
            
            unsafe {
                let mut token = windows::Win32::Foundation::HANDLE::default();
                let process = GetCurrentProcess();
                
                if OpenProcessToken(process, TOKEN_QUERY, &mut token).is_err() {
                    return Err(anyhow::anyhow!("プロセストークンの取得に失敗しました"));
                }
                
                let mut elevation = TOKEN_ELEVATION { TokenIsElevated: BOOL(0) };
                let mut return_length = 0u32;
                
                if GetTokenInformation(
                    token,
                    TokenElevation,
                    Some(&mut elevation as *mut _ as *mut _),
                    std::mem::size_of::<TOKEN_ELEVATION>() as u32,
                    &mut return_length,
                ).is_err() {
                    return Err(anyhow::anyhow!("トークン情報の取得に失敗しました"));
                }
                
                if elevation.TokenIsElevated.0 == 0 {
                    return Err(anyhow::anyhow!(
                        "管理者権限が必要です。アプリケーションを右クリックして「管理者として実行」してください。"
                    ));
                }
            }
        }
        
        Ok(())
    }

    pub async fn start(self, db: Arc<Mutex<Database>>) -> Result<()> {
        // 管理者権限チェック
        Self::check_admin_privileges()
            .context("管理者権限がありません")?;

        self.running.store(true, Ordering::SeqCst);
        info!("パケットキャプチャを開始します");

        // 別スレッドでキャプチャを実行（ブロッキング処理のため）
        let running = Arc::clone(&self.running);
        tokio::task::spawn_blocking(move || {
            if let Err(e) = Self::capture_loop_blocking(running, db) {
                error!("パケットキャプチャエラー: {}", e);
            }
        });

        Ok(())
    }

    fn capture_loop_blocking(
        running: Arc<AtomicBool>,
        db: Arc<Mutex<Database>>,
    ) -> Result<()> {
        info!("WinDivertを初期化中...");
        
        // WinDivertフィルタ
        // まずはすべてのTCPパケットをキャプチャ（後で特定のサーバーに絞る）
        let filter = create_windivert_filter();
        info!("フィルタ: {}", filter);

        // WinDivertを開く（SNIFFモードでゲームに影響を与えない）
        let divert = WinDivert::open(
            &filter,
            WINDIVERT_LAYER_NETWORK,
            0,
            WINDIVERT_FLAG_SNIFF,
        ).context("WinDivertの開始に失敗。管理者権限で実行していますか？")?;

        info!("パケットキャプチャ開始。取引所を開いてください...");

        let parser = PacketParser::new();
        let mut buffer = vec![0u8; 65535];
        let mut packet_count = 0u64;
        let mut market_packet_count = 0u64;

        loop {
            // 停止フラグをチェック
            if !running.load(Ordering::SeqCst) {
                info!("パケットキャプチャを停止します");
                break;
            }

            // パケットを受信
            let mut addr = WinDivertAddress::default();
            let recv_len = match divert.recv(&mut buffer, &mut addr) {
                Ok(len) => len,
                Err(e) => {
                    warn!("パケット受信エラー: {}", e);
                    continue;
                }
            };

            packet_count += 1;
            
            // 100パケットごとにログ出力
            if packet_count % 100 == 0 {
                debug!("受信パケット数: {}, 取引所パケット数: {}", packet_count, market_packet_count);
            }

            let packet_data = &buffer[..recv_len];

            // TCPペイロードを抽出
            let payload = match extract_tcp_payload(packet_data) {
                Some(p) if !p.is_empty() => p,
                _ => continue,
            };

            // デバッグ: 最初の数バイトをログ出力
            if payload.len() >= 4 {
                debug!(
                    "ペイロード先頭: {:02X} {:02X} {:02X} {:02X} (長さ: {})",
                    payload[0], payload[1], payload[2], payload[3], payload.len()
                );
            }

            // パケットを解析
            let raw_packet = RawPacketData {
                timestamp: Utc::now(),
                source_ip: String::new(),
                dest_ip: String::new(),
                source_port: 0,
                dest_port: 0,
                payload: payload.to_vec(),
            };

            match parser.parse(&raw_packet) {
                Ok(Some(market_packet)) => {
                    market_packet_count += 1;
                    info!("取引所パケットを検出！ アイテム数: {}", market_packet.items.len());

                    // データベースに保存
                    let db_clone = db.clone();
                    tokio::spawn(async move {
                        let db = db_clone.lock().await;
                        for item in market_packet.items {
                            if let Err(e) = db.insert_market_item(&item) {
                                error!("アイテムの保存に失敗: {}", e);
                            } else {
                                info!("アイテムを保存: {} - {}G", item.name, item.price);
                            }
                        }
                    });
                }
                Ok(None) => {
                    // 取引所パケットではない
                }
                Err(e) => {
                    debug!("パケット解析エラー: {}", e);
                }
            }
        }

        info!(
            "パケットキャプチャ終了。総パケット数: {}, 取引所パケット数: {}",
            packet_count, market_packet_count
        );

        Ok(())
    }

    pub async fn stop(self) -> Result<()> {
        self.running.store(false, Ordering::SeqCst);
        info!("パケットキャプチャの停止を要求しました");
        Ok(())
    }
}

// WinDivertの実装のためのヘルパー関数

/// Blue Protocolのサーバーを識別するためのフィルタ
fn create_windivert_filter() -> String {
    // TODO: Blue Protocol: Star Resonanceの実際のサーバーIPとポートに合わせて調整
    // 
    // 現在は全てのTCPトラフィックをキャプチャ
    // 実際の運用では特定のサーバーIPに絞る:
    // 例: "tcp and (remoteAddr == 123.45.67.89 or remoteAddr == 123.45.67.90)"
    // 
    // ゲームサーバーのIPアドレスは以下の方法で特定:
    // 1. Wiresharkでゲーム起動時のトラフィックを監視
    // 2. netstat -an でゲームの接続先を確認
    // 3. BPSR Logsのコードを参照
    
    // 開発用：すべてのTCPパケット
    "tcp".to_string()
}

/// TCPペイロードを抽出
fn extract_tcp_payload(packet: &[u8]) -> Option<&[u8]> {
    use etherparse::SlicedPacket;
    
    match SlicedPacket::from_ip(packet) {
        Ok(sliced) => {
            if let Some(tcp) = sliced.transport {
                if let etherparse::TransportSlice::Tcp(tcp_header) = tcp {
                    // TCPヘッダーのサイズを計算
                    let tcp_header_len = tcp_header.data_offset() as usize * 4;
                    let payload_offset = sliced.ip.unwrap().header_len() + tcp_header_len;
                    
                    if payload_offset < packet.len() {
                        return Some(&packet[payload_offset..]);
                    }
                }
            }
            None
        }
        Err(_) => None,
    }
}
