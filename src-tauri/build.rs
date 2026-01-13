fn main() {
    // WinDivertのリンク設定
    #[cfg(windows)]
    {
        // WinDivert.dllがあるディレクトリをリンカーに伝える
        let manifest_dir = std::env::var("CARGO_MANIFEST_DIR").unwrap();
        println!("cargo:rustc-link-search=native={}", manifest_dir);
        println!("cargo:rustc-link-lib=dylib=WinDivert");
        
        // リソースファイルのパスを再ビルド時に監視
        println!("cargo:rerun-if-changed=WinDivert.dll");
        println!("cargo:rerun-if-changed=WinDivert64.sys");
    }
    
    tauri_build::build()
}
