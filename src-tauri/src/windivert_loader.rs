/// WinDivert動的ロードヘルパー
/// 
/// libloadingを使用してWinDivert64.dllを動的にロードする

use anyhow::{Result, anyhow};
use once_cell::sync::OnceCell;
use std::path::PathBuf;

static WINDIVERT_PATH: OnceCell<PathBuf> = OnceCell::new();

/// WinDivertライブラリのパスを取得
pub fn get_windivert_path() -> Result<PathBuf> {
    if let Some(path) = WINDIVERT_PATH.get() {
        return Ok(path.clone());
    }

    // 実行ファイルと同じディレクトリを確認
    let exe_dir = std::env::current_exe()?
        .parent()
        .ok_or_else(|| anyhow!("実行ファイルのディレクトリを取得できません"))?
        .to_path_buf();

    let windivert_dll = exe_dir.join("WinDivert64.dll");
    
    if windivert_dll.exists() {
        let _ = WINDIVERT_PATH.set(windivert_dll.clone());
        return Ok(windivert_dll);
    }

    // 開発環境: src-tauriディレクトリを確認
    let dev_path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("WinDivert64.dll");
    if dev_path.exists() {
        let _ = WINDIVERT_PATH.set(dev_path.clone());
        return Ok(dev_path);
    }

    // カレントディレクトリを確認
    let current_path = PathBuf::from("WinDivert64.dll");
    if current_path.exists() {
        let _ = WINDIVERT_PATH.set(current_path.clone());
        return Ok(current_path);
    }

    Err(anyhow!(
        "WinDivert64.dllが見つかりません。以下の場所を確認してください:\n\
         1. {}\n\
         2. {}\n\
         3. カレントディレクトリ",
        windivert_dll.display(),
        dev_path.display()
    ))
}

/// WinDivertドライバーのパスを取得
pub fn get_windivert_sys_path() -> Result<PathBuf> {
    let dll_path = get_windivert_path()?;
    let sys_path = dll_path
        .parent()
        .ok_or_else(|| anyhow!("親ディレクトリを取得できません"))?
        .join("WinDivert64.sys");

    if !sys_path.exists() {
        return Err(anyhow!(
            "WinDivert64.sysが見つかりません: {}",
            sys_path.display()
        ));
    }

    Ok(sys_path)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[ignore] // CI環境では実行しない
    fn test_find_windivert() {
        let result = get_windivert_path();
        match result {
            Ok(path) => println!("WinDivert found at: {}", path.display()),
            Err(e) => println!("WinDivert not found: {}", e),
        }
    }
}
