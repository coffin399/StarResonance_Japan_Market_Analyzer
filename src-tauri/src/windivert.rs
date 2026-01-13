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

// WinDivert関数の外部宣言
#[cfg(windows)]
extern "C" {
    fn WinDivertOpen(filter: *const c_char, layer: c_int, priority: i16, flags: u64) -> *mut c_void;
    fn WinDivertClose(handle: *mut c_void) -> bool;
    fn WinDivertRecv(
        handle: *mut c_void,
        packet: *mut u8,
        packet_len: u32,
        recv_len: *mut u32,
        addr: *mut WinDivertAddress,
    ) -> bool;
    fn WinDivertSend(
        handle: *mut c_void,
        packet: *const u8,
        packet_len: u32,
        send_len: *mut u32,
        addr: *const WinDivertAddress,
    ) -> bool;
    fn WinDivertHelperParsePacket(
        packet: *const u8,
        packet_len: u32,
        ip_hdr: *mut *mut c_void,
        ip6_hdr: *mut *mut c_void,
        icmp_hdr: *mut *mut c_void,
        icmpv6_hdr: *mut *mut c_void,
        tcp_hdr: *mut *mut c_void,
        udp_hdr: *mut *mut c_void,
        data: *mut *mut c_void,
        data_len: *mut u32,
    ) -> bool;
}

/// WinDivertハンドル
pub struct WinDivert {
    handle: *mut c_void,
}

impl WinDivert {
    /// WinDivertを開く
    pub fn open(filter: &str, layer: i32, priority: i16, flags: u64) -> Result<Self> {
        #[cfg(windows)]
        {
            let filter_cstr = CString::new(filter)?;
            
            unsafe {
                let handle = WinDivertOpen(filter_cstr.as_ptr(), layer, priority, flags);
                
                if handle.is_null() {
                    return Err(anyhow!("WinDivertの開始に失敗しました。管理者権限で実行していますか？"));
                }
                
                Ok(WinDivert { handle })
            }
        }
        
        #[cfg(not(windows))]
        {
            Err(anyhow!("WinDivertはWindowsでのみ利用可能です"))
        }
    }

    /// パケットを受信
    pub fn recv(&self, buffer: &mut [u8], addr: &mut WinDivertAddress) -> Result<usize> {
        #[cfg(windows)]
        {
            let mut recv_len: u32 = 0;
            
            unsafe {
                let success = WinDivertRecv(
                    self.handle,
                    buffer.as_mut_ptr(),
                    buffer.len() as u32,
                    &mut recv_len,
                    addr as *mut WinDivertAddress,
                );
                
                if !success {
                    return Err(anyhow!("パケットの受信に失敗しました"));
                }
                
                Ok(recv_len as usize)
            }
        }
        
        #[cfg(not(windows))]
        {
            Err(anyhow!("WinDivertはWindowsでのみ利用可能です"))
        }
    }

    /// パケットを送信（再注入）
    pub fn send(&self, packet: &[u8], addr: &WinDivertAddress) -> Result<usize> {
        #[cfg(windows)]
        {
            let mut send_len: u32 = 0;
            
            unsafe {
                let success = WinDivertSend(
                    self.handle,
                    packet.as_ptr(),
                    packet.len() as u32,
                    &mut send_len,
                    addr as *const WinDivertAddress,
                );
                
                if !success {
                    return Err(anyhow!("パケットの送信に失敗しました"));
                }
                
                Ok(send_len as usize)
            }
        }
        
        #[cfg(not(windows))]
        {
            Err(anyhow!("WinDivertはWindowsでのみ利用可能です"))
        }
    }

    /// パケットをパース（TCPペイロードを取得）
    #[allow(dead_code)]
    pub fn parse_packet(&self, packet: &[u8]) -> Result<Option<PacketInfo>> {
        #[cfg(windows)]
        {
            use std::ptr;
            
            let mut ip_hdr: *mut c_void = ptr::null_mut();
            let mut ip6_hdr: *mut c_void = ptr::null_mut();
            let mut icmp_hdr: *mut c_void = ptr::null_mut();
            let mut icmpv6_hdr: *mut c_void = ptr::null_mut();
            let mut tcp_hdr: *mut c_void = ptr::null_mut();
            let mut udp_hdr: *mut c_void = ptr::null_mut();
            let mut data: *mut c_void = ptr::null_mut();
            let mut data_len: u32 = 0;
            
            unsafe {
                let success = WinDivertHelperParsePacket(
                    packet.as_ptr(),
                    packet.len() as u32,
                    &mut ip_hdr,
                    &mut ip6_hdr,
                    &mut icmp_hdr,
                    &mut icmpv6_hdr,
                    &mut tcp_hdr,
                    &mut udp_hdr,
                    &mut data,
                    &mut data_len,
                );
                
                if !success || tcp_hdr.is_null() {
                    return Ok(None);
                }
                
                // TCPペイロードを取得
                if data_len > 0 && !data.is_null() {
                    let payload = std::slice::from_raw_parts(data as *const u8, data_len as usize);
                    
                    Ok(Some(PacketInfo {
                        payload: payload.to_vec(),
                    }))
                } else {
                    Ok(None)
                }
            }
        }
        
        #[cfg(not(windows))]
        {
            Err(anyhow!("WinDivertはWindowsでのみ利用可能です"))
        }
    }
}

impl Drop for WinDivert {
    fn drop(&mut self) {
        #[cfg(windows)]
        unsafe {
            WinDivertClose(self.handle);
        }
    }
}

// WinDivertは内部で適切な同期を行っているため、Sendは安全
unsafe impl Send for WinDivert {}

#[derive(Debug, Clone)]
pub struct PacketInfo {
    pub payload: Vec<u8>,
}
