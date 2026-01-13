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

    pub fn get_running(&self) -> Arc<AtomicBool> {
        Arc::clone(&self.running)
    }

    fn check_admin_privileges() -> Result<()> {
        #[cfg(windows)]
        {
            use windows::Win32::Security::{GetTokenInformation, TokenElevation, TOKEN_ELEVATION, TOKEN_QUERY};
            use windows::Win32::System::Threading::{GetCurrentProcess, OpenProcessToken};
            
            unsafe {
                let mut token = windows::Win32::Foundation::HANDLE::default();
                let process = GetCurrentProcess();
                
                if OpenProcessToken(process, TOKEN_QUERY, &mut token).is_err() {
                    return Err(anyhow::anyhow!("Failed to get process token"));
                }
                
                let mut elevation = TOKEN_ELEVATION { TokenIsElevated: 0 };
                let mut return_length = 0u32;
                
                if GetTokenInformation(
                    token,
                    TokenElevation,
                    Some(&mut elevation as *mut _ as *mut _),
                    std::mem::size_of::<TOKEN_ELEVATION>() as u32,
                    &mut return_length,
                ).is_err() {
                    return Err(anyhow::anyhow!("Failed to get token information"));
                }
                
                if elevation.TokenIsElevated == 0 {
                    return Err(anyhow::anyhow!(
                        "Administrator privileges required. Please right-click and select 'Run as administrator'."
                    ));
                }
            }
        }
        
        Ok(())
    }

    pub async fn run_capture(running: Arc<AtomicBool>, db: Arc<Mutex<Database>>) -> Result<()> {
        // 管理者権限チェック
        Self::check_admin_privileges()
            .context("No administrator privileges")?;

        running.store(true, Ordering::SeqCst);
        info!("Starting packet capture");

        // 別スレッドでキャプチャを実行（ブロッキング処理のため）
        tokio::task::spawn_blocking(move || {
            if let Err(e) = Self::capture_loop_blocking(running, db) {
                error!("Packet capture error: {}", e);
            }
        });

        Ok(())
    }

    fn capture_loop_blocking(
        running: Arc<AtomicBool>,
        db: Arc<Mutex<Database>>,
    ) -> Result<()> {
        info!("Initializing WinDivert...");
        
        // WinDivert filter
        // Capture all TCP packets first (later narrow down to specific servers)
        let filter = create_windivert_filter();
        info!("Filter: {}", filter);

        // Open WinDivert (SNIFF mode to not affect the game)
        let divert = WinDivert::open(
            &filter,
            WINDIVERT_LAYER_NETWORK,
            0,
            WINDIVERT_FLAG_SNIFF,
        ).context("Failed to start WinDivert. Are you running as administrator?")?;

        info!("Packet capture started. Please open the market in game...");

        let parser = PacketParser::new();
        let mut buffer = vec![0u8; 65535];
        let mut packet_count = 0u64;
        let mut market_packet_count = 0u64;

        loop {
            // Check stop flag
            if !running.load(Ordering::SeqCst) {
                info!("Stopping packet capture");
                break;
            }

            // Receive packet
            let mut addr = WinDivertAddress::default();
            let recv_len = match divert.recv(&mut buffer, &mut addr) {
                Ok(len) => len,
                Err(e) => {
                    warn!("Packet receive error: {}", e);
                    continue;
                }
            };

            packet_count += 1;
            
            // Log every 100 packets
            if packet_count % 100 == 0 {
                debug!("Packets received: {}, Market packets: {}", packet_count, market_packet_count);
            }

            let packet_data = &buffer[..recv_len];

            // Extract TCP payload
            let payload = match extract_tcp_payload(packet_data) {
                Some(p) if !p.is_empty() => p,
                _ => continue,
            };

            // Debug: log first few bytes
            if payload.len() >= 4 {
                debug!(
                    "Payload header: {:02X} {:02X} {:02X} {:02X} (length: {})",
                    payload[0], payload[1], payload[2], payload[3], payload.len()
                );
            }

            // Parse packet
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
                    info!("Market packet detected! Items: {}", market_packet.items.len());

                    // Save to database
                    let db_clone = db.clone();
                    tokio::spawn(async move {
                        let db = db_clone.lock().await;
                        for item in market_packet.items {
                            if let Err(e) = db.insert_market_item(&item) {
                                error!("Failed to save item: {}", e);
                            } else {
                                info!("Item saved: {} - {}G", item.name, item.price);
                            }
                        }
                    });
                }
                Ok(None) => {
                    // Not a market packet
                }
                Err(e) => {
                    debug!("Packet parse error: {}", e);
                }
            }
        }

        info!(
            "Packet capture ended. Total packets: {}, Market packets: {}",
            packet_count, market_packet_count
        );

        Ok(())
    }

    pub async fn stop(self) -> Result<()> {
        self.running.store(false, Ordering::SeqCst);
        info!("Packet capture stop requested");
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

/// Extract TCP payload
fn extract_tcp_payload(packet: &[u8]) -> Option<&[u8]> {
    use etherparse::SlicedPacket;
    
    match SlicedPacket::from_ip(packet) {
        Ok(sliced) => {
            // etherparse automatically extracts the payload
            // Check if we have TCP transport layer
            if let Some(etherparse::TransportSlice::Tcp(_)) = sliced.transport {
                // Return the payload if it exists
                if let Some(payload) = sliced.payload.payload {
                    if !payload.is_empty() {
                        return Some(payload);
                    }
                }
            }
            None
        }
        Err(_) => None,
    }
}
