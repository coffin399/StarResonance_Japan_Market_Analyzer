/// WinDivert FFI バインディング
/// 
/// WinDivert C APIをRustから呼び出すためのFFIラッパー

use std::ffi::CString;
use std::os::raw::{c_char, c_int, c_void};
use anyhow::{Result, anyhow};

// WinDivertのフラグとパラメータ
pub const WINDIVERT_FLAG_SNIFF: u64 = 1;
pub const WINDIVERT_FLAG_DROP: u64 = 2;
pub const WINDIVERT_FLAG_RECV_ONLY: u64 = 4;
pub const WINDIVERT_FLAG_SEND_ONLY: u64 = 8;

pub const WINDIVERT_LAYER_NETWORK: i32 = 0;
pub const WINDIVERT_LAYER_NETWORK_FORWARD: i32 = 1;

// WinDivertAddress構造体
#[repr(C)]
#[derive(Debug, Clone, Copy)]
pub struct WinDivertAddress {
    pub timestamp: i64,
    pub layer: u8,
    pub event: u8,
    pub sniffed: u8,
    pub outbound: u8,
    pub loopback: u8,
    pub impostor: u8,
    pub ipv6: u8,
    pub ip_checksum: u8,
    pub tcp_checksum: u8,
    pub udp_checksum: u8,
    pub reserved1: [u8; 3],
    pub if_idx: u32,
    pub sub_if_idx: u32,
    pub reserved2: [u32; 2],
}

impl Default for WinDivertAddress {
    fn default() -> Self {
        unsafe { std::mem::zeroed() }
    }
}

// WinDivert will be loaded dynamically at runtime using libloading
// No need for extern declarations

/// WinDivertハンドル (stub for now - will implement dynamic loading)
pub struct WinDivert {
    _handle: *mut c_void,
}

impl WinDivert {
    /// WinDivertを開く (stub implementation - actual implementation coming soon)
    pub fn open(_filter: &str, _layer: i32, _priority: i16, _flags: u64) -> Result<Self> {
        #[cfg(windows)]
        {
            // TODO: Implement dynamic loading of WinDivert.dll using libloading
            // For now, return error with helpful message
            return Err(anyhow!(
                "WinDivert dynamic loading not yet implemented.\n\
                 This is a work-in-progress feature.\n\
                 The application will compile but packet capture is not functional yet."
            ));
        }
        
        #[cfg(not(windows))]
        {
            Err(anyhow!("WinDivert is only available on Windows"))
        }
    }

    /// パケットを受信 (stub)
    pub fn recv(&self, _buffer: &mut [u8], _addr: &mut WinDivertAddress) -> Result<usize> {
        Err(anyhow!("WinDivert not yet implemented"))
    }
}

impl Drop for WinDivert {
    fn drop(&mut self) {
        // TODO: Implement cleanup when dynamic loading is done
    }
}

// WinDivertは内部で適切な同期を行っているため、Sendは安全
unsafe impl Send for WinDivert {}

#[derive(Debug, Clone)]
pub struct PacketInfo {
    pub payload: Vec<u8>,
}
