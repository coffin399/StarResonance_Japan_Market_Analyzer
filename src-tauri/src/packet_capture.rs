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
        
        let filter = create_windivert_filter();
        info!("Filter: {}", filter);

        // Open WinDivert (SNIFF mode to not affect the game)
        let divert = WinDivert::open(
            &filter,
            WINDIVERT_LAYER_NETWORK,
            0,
            WINDIVERT_FLAG_SNIFF,
        ).context("Failed to start WinDivert. Are you running as administrator?")?;

        info!("Packet capture started. Waiting for game server...");

        let mut buffer = vec![0u8; 10 * 1024 * 1024]; // 10MB buffer like BPSR Logs
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

            let source_ip = ipv4.header().source();
            let dest_ip = ipv4.header().destination();
            let source_port = tcp.source_port();
            let dest_port = tcp.destination_port();
            let tcp_payload = tcp.payload();
            let seq_number = tcp.sequence_number() as usize;

            let current_server = GameServer::new(source_ip, source_port, dest_ip, dest_port);

            // Try to identify game server
            if known_server != Some(current_server) {
                // Method 1: Check for game server signature
                if Self::check_game_signature(tcp_payload) {
                    info!("Game server detected (by signature): {}:{} -> {}:{}", 
                        source_ip, source_port, dest_ip, dest_port);
                    known_server = Some(current_server);
                    tcp_reassembler.clear(seq_number + tcp_payload.len());
                    continue;
                }

                // Method 2: Check for login packet
                if Self::check_login_packet(tcp_payload) {
                    info!("Game server detected (by login): {}:{} -> {}:{}", 
                        source_ip, source_port, dest_ip, dest_port);
                    known_server = Some(current_server);
                    tcp_reassembler.clear(seq_number + tcp_payload.len());
                    continue;
                }

                continue;
            }

            // Process packets from known server
            if tcp_payload.is_empty() {
                continue;
            }

            // Add to TCP reassembler
            tcp_reassembler.add_packet(seq_number, tcp_payload.to_vec());
            tcp_reassembler.reassemble();

            // Extract complete packets
            while let Some(packet_data) = tcp_reassembler.extract_packet() {
                game_packet_count += 1;
                
                match Self::process_game_packet(&packet_data, &db) {
                    Ok(true) => {
                        debug!("Game packet processed successfully");
                    }
                    Ok(false) => {
                        // Not a market packet
                    }
                    Err(e) => {
                        debug!("Failed to process packet: {}", e);
                    }
                }
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
        if payload.len() < 10 {
            return false;
        }

        // Check for fragmentated packet structure
        if payload[4] != 0 {
            return false;
        }

        let mut offset = 0;
        while offset + 4 <= payload.len() {
            if offset > 1000 {
                break; // Prevent infinite loop
            }

            let frag_len = u32::from_le_bytes([
                payload[offset],
                payload[offset + 1],
                payload[offset + 2],
                payload[offset + 3],
            ]) as usize;

            if frag_len < 4 {
                break;
            }

            let payload_len = frag_len.saturating_sub(4);
            offset += 4;

            if offset + payload_len > payload.len() {
                break;
            }

            let fragment = &payload[offset..offset + payload_len];
            if fragment.len() >= 5 + GAME_SERVER_SIGNATURE.len() 
                && fragment[5..5 + GAME_SERVER_SIGNATURE.len()] == GAME_SERVER_SIGNATURE {
                return true;
            }

            offset += payload_len;
        }

        false
    }

    /// Check if this is a login packet
    fn check_login_packet(payload: &[u8]) -> bool {
        payload.len() == LOGIN_PACKET_SIZE
            && payload.len() >= 20
            && payload[0..10] == LOGIN_SIGNATURE_1
            && payload[14..20] == LOGIN_SIGNATURE_2
    }

    /// Process a complete game packet
    fn process_game_packet(data: &[u8], _db: &Arc<Mutex<Database>>) -> Result<bool> {
        let packet = GamePacket::parse(data)?;
        
        debug!("Game packet: type={:04X}, compressed={}, size={}", 
            packet.packet_type, packet.is_compressed, packet.size);

        // TODO: Parse market-specific packets
        // For now, just log the packet
        
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

