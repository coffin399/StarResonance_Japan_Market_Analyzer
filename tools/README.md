# Tools Directory

This directory contains utilities for packet capture and analysis.

## Files

### packet_parser.py
Main parser for extracting trading data from PCAP files.

### parse-pcap.bat
Simple batch script to parse a single PCAP file.

**Usage:**
```bat
REM Drag and drop
parse-pcap.bat

REM Or specify file
parse-pcap.bat capture.pcap
```

### analyze-traffic.bat
Interactive tool for analyzing game traffic.

**Features:**
- Parse existing PCAP files
- List network interfaces
- Live packet capture (requires admin)
- Search for magic bytes

## Common Warnings (IGNORE THESE)

When using these tools, you may see warnings like:

```
WARNING: Wireshark is installed, but cannot read manuf !
```
**This is normal and can be ignored.** It doesn't affect functionality.

```
CryptographyDeprecationWarning: TripleDES has been moved...
```
**This is also normal.** These warnings are suppressed in the code but may still appear in some cases.

## Requirements

- Virtual environment must be activated
- Run `quick-install.bat` first to install all dependencies including scapy

## Troubleshooting

### "No module named 'scapy'"
→ Run `quick-install.bat` to install dependencies

### "Virtual environment not found"
→ Run `quick-install.bat` first

### Admin privileges required
Live capture requires administrator privileges. Run the command prompt as administrator.
