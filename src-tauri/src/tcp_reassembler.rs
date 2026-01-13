/// TCP Packet Reassembler
/// 
/// Based on BPSR Logs implementation
/// https://github.com/winjwinj/bpsr-logs

use std::collections::BTreeMap;

#[derive(Debug)]
pub struct TCPReassembler {
    pub next_seq: Option<usize>,
    pub cache: BTreeMap<usize, Vec<u8>>,
    pub data: Vec<u8>,
}

impl TCPReassembler {
    pub fn new() -> Self {
        Self {
            next_seq: None,
            cache: BTreeMap::new(),
            data: Vec::new(),
        }
    }

    pub fn clear(&mut self, seq: usize) {
        self.next_seq = Some(seq);
        self.cache.clear();
        self.data.clear();
    }

    pub fn add_packet(&mut self, seq: usize, payload: Vec<u8>) {
        if self.next_seq.is_none() {
            self.next_seq = Some(seq);
        }

        // Only cache packets that are not too far behind
        if let Some(next_seq) = self.next_seq {
            if next_seq.saturating_sub(seq) == 0 {
                self.cache.insert(seq, payload);
            }
        }
    }

    pub fn reassemble(&mut self) -> bool {
        let Some(mut next_seq) = self.next_seq else {
            return false;
        };

        let mut progress = false;
        while let Some(cached_data) = self.cache.remove(&next_seq) {
            if self.data.is_empty() {
                self.data = cached_data.clone();
            } else {
                self.data.extend_from_slice(&cached_data);
            }
            next_seq = next_seq.wrapping_add(cached_data.len());
            self.next_seq = Some(next_seq);
            progress = true;
        }

        progress
    }

    pub fn extract_packet(&mut self) -> Option<Vec<u8>> {
        if self.data.len() < 4 {
            tracing::debug!("extract_packet: not enough data ({} bytes)", self.data.len());
            return None;
        }

        // Read packet size (first 4 bytes, little-endian)
        let packet_size = u32::from_le_bytes([
            self.data[0],
            self.data[1],
            self.data[2],
            self.data[3],
        ]) as usize;

        tracing::debug!("extract_packet: packet_size={}, data_len={}", packet_size, self.data.len());

        // パケットサイズの妥当性チェック
        if packet_size < 6 {
            tracing::warn!("extract_packet: packet_size too small ({}), clearing buffer", packet_size);
            // 異常なパケットサイズの場合、バッファをクリア
            self.data.clear();
            return None;
        }
        
        if packet_size > 1024 * 1024 {
            tracing::warn!("extract_packet: packet_size too large ({}), clearing buffer", packet_size);
            // 1MB以上は異常
            self.data.clear();
            return None;
        }

        if self.data.len() < packet_size {
            tracing::debug!("extract_packet: waiting for more data (need {} more bytes)", 
                packet_size - self.data.len());
            return None;
        }

        // Extract packet
        tracing::info!("✅ Extracting packet: size={}", packet_size);
        let packet = self.data[..packet_size].to_vec();
        self.data = self.data[packet_size..].to_vec();
        tracing::debug!("extract_packet: remaining data_len={}", self.data.len());

        Some(packet)
    }
}

impl Default for TCPReassembler {
    fn default() -> Self {
        Self::new()
    }
}
