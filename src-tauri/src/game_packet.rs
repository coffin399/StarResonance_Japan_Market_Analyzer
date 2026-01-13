/// Game Packet Parser
/// 
/// Based on BPSR Logs implementation
/// https://github.com/winjwinj/bpsr-logs

use anyhow::{Result, anyhow};

// Game server signature from BPSR Logs
pub const GAME_SERVER_SIGNATURE: [u8; 6] = [0x00, 0x63, 0x33, 0x53, 0x42, 0x00];
pub const SERVICE_UUID: u64 = 0x0000000063335342;

// Login packet signature
pub const LOGIN_SIGNATURE_1: [u8; 10] = [0x00, 0x00, 0x00, 0x62, 0x00, 0x03, 0x00, 0x00, 0x00, 0x01];
pub const LOGIN_SIGNATURE_2: [u8; 6] = [0x00, 0x00, 0x00, 0x00, 0x0a, 0x4e];
pub const LOGIN_PACKET_SIZE: usize = 98;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FragmentType {
    Notify = 0,
    FrameDown = 1,
    Unknown,
}

impl From<u16> for FragmentType {
    fn from(value: u16) -> Self {
        match value {
            0 => FragmentType::Notify,
            1 => FragmentType::FrameDown,
            _ => FragmentType::Unknown,
        }
    }
}

#[derive(Debug)]
pub struct GamePacket {
    pub size: u32,
    pub packet_type: u16,
    pub is_compressed: bool,
    pub fragment_type: FragmentType,
    pub payload: Vec<u8>,
}

impl GamePacket {
    /// Parse a game packet from raw bytes
    pub fn parse(data: &[u8]) -> Result<Self> {
        if data.len() < 6 {
            return Err(anyhow!("Packet too small: {} bytes", data.len()));
        }

        // Read packet size (4 bytes, little-endian)
        let size = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);

        // Read packet type (2 bytes, little-endian)
        let packet_type = u16::from_le_bytes([data[4], data[5]]);

        // Check compression flag (bit 15)
        let is_compressed = (packet_type & 0x8000) != 0;

        // Get fragment type (bits 0-14)
        let fragment_type = FragmentType::from(packet_type & 0x7fff);

        // Get payload
        let payload = if data.len() > 6 {
            data[6..].to_vec()
        } else {
            Vec::new()
        };

        Ok(Self {
            size,
            packet_type,
            is_compressed,
            fragment_type,
            payload,
        })
    }

    /// Check if payload contains game server signature
    pub fn has_game_signature(payload: &[u8]) -> bool {
        if payload.len() < 5 + GAME_SERVER_SIGNATURE.len() {
            return false;
        }
        &payload[5..5 + GAME_SERVER_SIGNATURE.len()] == GAME_SERVER_SIGNATURE
    }

    /// Check if this is a login packet
    pub fn is_login_packet(payload: &[u8]) -> bool {
        payload.len() == LOGIN_PACKET_SIZE
            && payload.len() >= 20
            && payload[0..10] == LOGIN_SIGNATURE_1
            && payload[14..20] == LOGIN_SIGNATURE_2
    }

    /// Parse Notify packet
    pub fn parse_notify(&self) -> Result<NotifyPacket> {
        let payload = &self.payload;
        if payload.len() < 16 {
            return Err(anyhow!("Notify payload too small"));
        }

        // Read service UUID (8 bytes, little-endian)
        let service_uuid = u64::from_le_bytes([
            payload[0], payload[1], payload[2], payload[3],
            payload[4], payload[5], payload[6], payload[7],
        ]);

        // Read stub ID (4 bytes) - not used
        let _stub_id = u32::from_le_bytes([
            payload[8], payload[9], payload[10], payload[11],
        ]);

        // Read method ID (4 bytes, little-endian)
        let method_id = u32::from_le_bytes([
            payload[12], payload[13], payload[14], payload[15],
        ]);

        // Get remaining data
        let data = if payload.len() > 16 {
            payload[16..].to_vec()
        } else {
            Vec::new()
        };

        Ok(NotifyPacket {
            service_uuid,
            method_id,
            data,
        })
    }
}

#[derive(Debug)]
pub struct NotifyPacket {
    pub service_uuid: u64,
    pub method_id: u32,
    pub data: Vec<u8>,
}

/// Decompress zstd data
pub fn decompress_zstd(data: &[u8]) -> Result<Vec<u8>> {
    zstd::decode_all(data).map_err(|e| anyhow!("zstd decompression failed: {}", e))
}
