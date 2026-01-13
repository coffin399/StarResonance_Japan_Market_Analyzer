use crate::database::Database;
use crate::tcp_reassembler::TCPReassembler;
use crate::game_packet::{GamePacket, GAME_SERVER_SIGNATURE, LOGIN_PACKET_SIZE, LOGIN_SIGNATURE_1, LOGIN_SIGNATURE_2};
use crate::windivert::{WinDivert, WinDivertAddress, WINDIVERT_FLAG_SNIFF, WINDIVERT_LAYER_NETWORK};
use anyhow::{Context, Result};
use etherparse::{SlicedPacket, NetSlice, TransportSlice};
use std::net::Ipv4Addr;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use tokio::sync::Mutex;
use tracing::{error, info, warn, debug};

pub struct PacketCapture {
    running: Arc<AtomicBool>,
}

impl PacketCapture {
    pub fn new() -> Result<Self> {
        info!("=== PacketCapture を初期化中 ===");

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
        info!("=== run_capture 開始 ===");
        
        // 管理者権限チェック
        info!("管理者権限をチェック中...");
        Self::check_admin_privileges()
            .context("No administrator privileges")?;
        info!("管理者権限: OK");

        running.store(true, Ordering::SeqCst);
        info!("running フラグを true に設定");

        // 別スレッドでキャプチャを実行（ブロッキング処理のため）
        info!("spawn_blocking でキャプチャスレッドを起動");
        tokio::task::spawn_blocking(move || {
            info!("=== capture_loop_blocking スレッド開始 ===");
            if let Err(e) = Self::capture_loop_blocking(running, db) {
                error!("Packet capture error: {}", e);
            } else {
                info!("=== capture_loop_blocking スレッド正常終了 ===");
            }
        });

        info!("=== run_capture 完了（スレッドは継続中） ===");
        Ok(())
    }

    fn capture_loop_blocking(
        running: Arc<AtomicBool>,
        db: Arc<Mutex<Database>>,
    ) -> Result<()> {
        info!("=== capture_loop_blocking: Initializing WinDivert ===");
        
        let filter = create_windivert_filter();
        info!("WinDivert Filter: {}", filter);

        info!("WinDivert::open を呼び出します...");
        // Open WinDivert (SNIFF mode to not affect the game)
        let divert = match WinDivert::open(
            &filter,
            WINDIVERT_LAYER_NETWORK,
            0,
            WINDIVERT_FLAG_SNIFF,
        ) {
            Ok(d) => {
                info!("✅ WinDivert::open 成功！");
                d
            }
            Err(e) => {
                error!("❌ WinDivert::open 失敗: {}", e);
                return Err(e).context("Failed to start WinDivert. Are you running as administrator?");
            }
        };

        info!("🎉 Packet capture started. Waiting for game server...");

        let mut buffer = vec![0u8; 10 * 1024 * 1024]; // 10MB buffer like BPSR Logs
        info!("Buffer allocated: {} MB", buffer.len() / 1024 / 1024);
        let mut known_server: Option<GameServer> = None;
        let mut tcp_reassembler = TCPReassembler::new();
        let mut packet_count = 0u64;
        let mut game_packet_count = 0u64;

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
            
            // Log every 1000 packets
            if packet_count % 1000 == 0 {
                debug!("Packets received: {}, Game packets: {}", packet_count, game_packet_count);
            }

            let packet_data = &buffer[..recv_len];

            // Parse IP and TCP layers
            let Ok(sliced) = SlicedPacket::from_ip(packet_data) else {
                continue;
            };

            let Some(NetSlice::Ipv4(ipv4)) = sliced.net else {
                continue;
            };

            let Some(TransportSlice::Tcp(tcp)) = sliced.transport else {
                continue;
            };

            let source_ip = Ipv4Addr::from(ipv4.header().source());
            let dest_ip = Ipv4Addr::from(ipv4.header().destination());
            let source_port = tcp.source_port();
            let dest_port = tcp.destination_port();
            let tcp_payload = tcp.payload();
            let seq_number = tcp.sequence_number() as usize;

            let current_server = GameServer::new(source_ip, source_port, dest_ip, dest_port);

            // Try to identify game server
            if known_server != Some(current_server) {
                // ペイロードがある場合のみチェック
                if !tcp_payload.is_empty() {
                    
                    // 定期的にサンプルパケットをログ出力
                    if packet_count % 500 == 0 {
                        debug!("Sample packet: {}:{} -> {}:{}, payload_len={}", 
                            source_ip, source_port, dest_ip, dest_port, tcp_payload.len());
                        if tcp_payload.len() >= 16 {
                            let preview: Vec<String> = tcp_payload[..16.min(tcp_payload.len())]
                                .iter()
                                .map(|b| format!("{:02X}", b))
                                .collect();
                            debug!("  Payload preview: {}", preview.join(" "));
                        }
                    }
                    
                    // Method 1: Check for game server signature
                    if Self::check_game_signature(tcp_payload) {
                        info!("🎮 Game server detected (by signature): {}:{} -> {}:{}", 
                            source_ip, source_port, dest_ip, dest_port);
                        known_server = Some(current_server);
                        tcp_reassembler.clear(seq_number + tcp_payload.len());
                        continue;
                    }

                    // Method 2: Check for login packet
                    if Self::check_login_packet(tcp_payload) {
                        info!("🎮 Game server detected (by login): {}:{} -> {}:{}", 
                            source_ip, source_port, dest_ip, dest_port);
                        known_server = Some(current_server);
                        tcp_reassembler.clear(seq_number + tcp_payload.len());
                        continue;
                    }
                }

                continue;
            }

            // Process packets from known server
            if tcp_payload.is_empty() {
                continue;
            }

            // デバッグ: ゲームサーバーからのパケットを記録
            if packet_count % 100 == 0 {
                debug!("Game server packet: seq={}, payload_len={}", seq_number, tcp_payload.len());
            }

            // Add to TCP reassembler
            tcp_reassembler.add_packet(seq_number, tcp_payload.to_vec());
            let reassembled = tcp_reassembler.reassemble();
            
            if reassembled && packet_count % 100 == 0 {
                debug!("TCP reassembler: data_len={}", tcp_reassembler.data.len());
            }

            // Extract complete packets
            let mut extracted_count = 0;
            while let Some(packet_data) = tcp_reassembler.extract_packet() {
                game_packet_count += 1;
                extracted_count += 1;
                
                debug!("Extracted packet #{}: size={}", game_packet_count, packet_data.len());
                
                match Self::process_game_packet(&packet_data, &db) {
                    Ok(true) => {
                        info!("✅ Game packet processed successfully");
                    }
                    Ok(false) => {
                        debug!("Packet processed (not market data)");
                    }
                    Err(e) => {
                        debug!("Failed to process packet: {}", e);
                    }
                }
            }
            
            if extracted_count > 0 {
                debug!("Extracted {} packets from reassembler", extracted_count);
            }
        }

        info!(
            "Packet capture ended. Total packets: {}, Game packets: {}",
            packet_count, game_packet_count
        );

        Ok(())
    }

    /// Check if payload contains game server signature
    fn check_game_signature(payload: &[u8]) -> bool {
        if payload.len() < 20 {
            return false;
        }

        // シンプルな検索: ペイロード内でシグネチャを探す
        // 実際のパケットでは offset 12-17 に "63 33 53 42" が含まれている
        for i in 0..payload.len().saturating_sub(6) {
            if i + 6 <= payload.len() 
                && &payload[i..i + 6] == &GAME_SERVER_SIGNATURE {
                debug!("✅ Game signature found at offset {}", i);
                return true;
            }
        }

        false
    }

    /// Check if this is a login packet
    fn check_login_packet(payload: &[u8]) -> bool {
        if payload.len() != LOGIN_PACKET_SIZE {
            return false;
        }
        
        if payload.len() >= 20 {
            let matches = payload[0..10] == LOGIN_SIGNATURE_1
                && payload[14..20] == LOGIN_SIGNATURE_2;
            
            if matches {
                debug!("✅ Login packet signature found");
            }
            
            return matches;
        }
        
        false
    }

    /// Process a complete game packet
    fn process_game_packet(data: &[u8], _db: &Arc<Mutex<Database>>) -> Result<bool> {
        let packet = GamePacket::parse(data)?;
        
        info!("📦 Game packet: type={:04X}, compressed={}, size={}", 
            packet.packet_type, packet.is_compressed, packet.size);

        // パケットの最初の64バイトをダンプ
        if packet.payload.len() > 0 {
            let preview_len = packet.payload.len().min(64);
            info!("   Payload preview ({} bytes):", packet.payload.len());
            for (i, chunk) in packet.payload[..preview_len].chunks(16).enumerate() {
                let hex: String = chunk.iter().map(|b| format!("{:02X} ", b)).collect();
                let ascii: String = chunk.iter().map(|b| {
                    if *b >= 32 && *b <= 126 { *b as char } else { '.' }
                }).collect();
                info!("   {:04X}: {} | {}", i * 16, hex, ascii);
            }
            if packet.payload.len() > preview_len {
                info!("   ... ({} more bytes)", packet.payload.len() - preview_len);
            }
        }

        // TODO: Parse market-specific packets
        
        Ok(false)
    }

    pub async fn stop(self) -> Result<()> {
        self.running.store(false, Ordering::SeqCst);
        info!("Packet capture stop requested");
        Ok(())
    }
}

// WinDivertの実装のためのヘルパー関数

/// Blue Protocolのサーバーを識別するためのフィルタ
/// Based on BPSR Logs implementation
fn create_windivert_filter() -> String {
    // BPSR Logsと同じフィルタ:
    // - ループバック以外の全TCP/IPパケットをキャプチャ
    // - ゲームサーバーはパケット内容で動的に識別
    "!loopback && ip && tcp".to_string()
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
struct GameServer {
    source_ip: Ipv4Addr,
    source_port: u16,
    dest_ip: Ipv4Addr,
    dest_port: u16,
}

impl GameServer {
    fn new(source_ip: Ipv4Addr, source_port: u16, dest_ip: Ipv4Addr, dest_port: u16) -> Self {
        Self {
            source_ip,
            source_port,
            dest_ip,
            dest_port,
        }
    }
}

