/// WinDivert FFI バインディング
/// 
/// WinDivert C APIをRustから呼び出すためのFFIラッパー

use std::ffi::CString;
use std::os::raw::{c_char, c_int, c_uint, c_void};
use anyhow::{Result, anyhow};
use libloading::{Library, Symbol};
use once_cell::sync::OnceCell;
use std::sync::Mutex;

// WinDivertのフラグとパラメータ
pub const WINDIVERT_FLAG_SNIFF: u64 = 1;
pub const WINDIVERT_FLAG_DROP: u64 = 2;
pub const WINDIVERT_FLAG_RECV_ONLY: u64 = 4;
pub const WINDIVERT_FLAG_SEND_ONLY: u64 = 8;

pub const WINDIVERT_LAYER_NETWORK: i32 = 0;
pub const WINDIVERT_LAYER_NETWORK_FORWARD: i32 = 1;

// WinDivert関数ポインタ型定義
type WinDivertOpenFn = unsafe extern "C" fn(
    filter: *const c_char,
    layer: c_int,
    priority: i16,
    flags: u64,
) -> *mut c_void;

type WinDivertRecvFn = unsafe extern "C" fn(
    handle: *mut c_void,
    packet: *mut c_void,
    packet_len: c_uint,
    recv_len: *mut c_uint,
    addr: *mut WinDivertAddress,
) -> c_int;

type WinDivertCloseFn = unsafe extern "C" fn(handle: *mut c_void) -> c_int;

// グローバルなWinDivertライブラリインスタンス
static WINDIVERT_LIB: OnceCell<Mutex<Library>> = OnceCell::new();

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

/// WinDivertライブラリをロード
fn load_windivert_library() -> Result<&'static Mutex<Library>> {
    WINDIVERT_LIB.get_or_try_init(|| {
        let dll_path = crate::windivert_loader::get_windivert_path()?;
        
        unsafe {
            let lib = Library::new(&dll_path)
                .map_err(|e| anyhow!("Failed to load WinDivert DLL: {}", e))?;
            
            tracing::info!("WinDivert DLL loaded from: {}", dll_path.display());
            Ok(Mutex::new(lib))
        }
    })
}

/// WinDivertハンドル
pub struct WinDivert {
    handle: *mut c_void,
}

impl WinDivert {
    /// WinDivertを開く
    pub fn open(filter: &str, layer: i32, priority: i16, flags: u64) -> Result<Self> {
        #[cfg(not(windows))]
        {
            return Err(anyhow!("WinDivert is only available on Windows"));
        }
        
        #[cfg(windows)]
        {
            let lib = load_windivert_library()?;
            let lib_guard = lib.lock().unwrap();
            
            let filter_c = CString::new(filter)?;
            
            unsafe {
                let open_fn: Symbol<WinDivertOpenFn> = lib_guard
                    .get(b"WinDivertOpen")
                    .map_err(|e| anyhow!("Failed to get WinDivertOpen: {}", e))?;
                
                let handle = open_fn(
                    filter_c.as_ptr(),
                    layer,
                    priority,
                    flags,
                );
                
                if handle.is_null() {
                    return Err(anyhow!(
                        "WinDivertOpen failed. Make sure:\n\
                         1. You are running as administrator\n\
                         2. WinDivert64.sys is in the same directory as WinDivert64.dll\n\
                         3. Windows version is compatible (Windows 7+)"
                    ));
                }
                
                tracing::info!("WinDivert opened successfully with filter: {}", filter);
                
                Ok(WinDivert { handle })
            }
        }
    }

    /// パケットを受信
    pub fn recv(&self, buffer: &mut [u8], addr: &mut WinDivertAddress) -> Result<usize> {
        let lib = load_windivert_library()?;
        let lib_guard = lib.lock().unwrap();
        
        unsafe {
            let recv_fn: Symbol<WinDivertRecvFn> = lib_guard
                .get(b"WinDivertRecv")
                .map_err(|e| anyhow!("Failed to get WinDivertRecv: {}", e))?;
            
            let mut recv_len: c_uint = 0;
            let result = recv_fn(
                self.handle,
                buffer.as_mut_ptr() as *mut c_void,
                buffer.len() as c_uint,
                &mut recv_len,
                addr as *mut WinDivertAddress,
            );
            
            if result == 0 {
                return Err(anyhow!("WinDivertRecv failed"));
            }
            
            Ok(recv_len as usize)
        }
    }
}

impl Drop for WinDivert {
    fn drop(&mut self) {
        if let Ok(lib) = load_windivert_library() {
            let lib_guard = lib.lock().unwrap();
            
            unsafe {
                if let Ok(close_fn) = lib_guard.get::<Symbol<WinDivertCloseFn>>(b"WinDivertClose") {
                    close_fn(self.handle);
                    tracing::info!("WinDivert handle closed");
                }
            }
        }
    }
}

// WinDivertは内部で適切な同期を行っているため、Sendは安全
unsafe impl Send for WinDivert {}

#[derive(Debug, Clone)]
pub struct PacketInfo {
    pub payload: Vec<u8>,
}
