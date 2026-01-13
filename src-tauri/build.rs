fn main() {
    // WinDivert is loaded at runtime via LoadLibrary
    // No need to link at compile time
    
    tauri_build::build()
}
