Here's the updated **README.md** with the new features and donation section:

# Pastebin Search Tool

A robust Bash script for security researchers to investigate data leaks on Pastebin across multiple search engines.  
Now with auto-update functionality, donation support, and enhanced security features.

## Features

- **Multi-Search Engine Support** - Google, Bing, DuckDuckGo, Yahoo
- **Auto-Update System** - Keep your tool current with `--update`
- **Enhanced Security** - SHA-1 checksum verification for safe updates
- **Browser Compatibility** - Supports Firefox, Chrome, Brave, Opera, Lynx
- **Professional Grade**:
  - POSIX-compliant option parsing
  - Input validation and sanitization
  - Clean temporary file handling
  - Graceful error recovery

## New in v2.0

- 🔄 Automatic updates
- 💰 Donation support
- 🛠 Improved error handling
- 🔒 SHA-1 verification
- 📚 Comprehensive help system

## Installation

### One-Line Install (Recommended)
```bash
curl -sSL https://raw.githubusercontent.com/byFranke/PastebinSearch/main/setup.sh | bash
```

### Manual Installation
```bash
git clone https://github.com/byfranke/pastebinsearch
cd pastebinsearch
chmod +x setup.sh
sudo ./setup.sh
```

## Usage

### Basic Search
```bash
pastebinsearch "credit card" credentials
```

### Specify Browser
```bash
pastebinsearch chromium "API_KEY" "password"
```

### Advanced Options
```bash
# Update tool
pastebinsearch --update

# Show version
pastebinsearch --version

# Display help
pastebinsearch --help

# Support development
pastebinsearch --donate
```

## Donation Support

This tool is maintained through community support. Help keep it active:

[![Donate](https://img.shields.io/badge/Support-Development-blue?style=for-the-badge&logo=github)](https://donate.stripe.com/28o8zQ2wY3Dr57G001)

```bash
# Display donation info
pastebinsearch --donate
```

## Key Functionality

1. **Smart Search**:
   - Automatic URL encoding
   - Parallel search across engines
   - 20-second timeout per request

2. **Security**:
   - Checksum verification
   - Input sanitization
   - Privilege separation

3. **Maintenance**:
   - One-command updates
   - Dependency checks
   - Clean uninstall

## Requirements

- **Bash 4.4+**
- **curl** (for updates)
- **Modern Web Browser**

## Ethical Guidelines

✔️ **Permitted Use**:
- Security research
- Data leak prevention
- Educational purposes

❌ **Prohibited Use**:
- Unauthorized access
- Malicious activities
- Privacy violations

```bash
# Verify installation
pastebinsearch --version
```

## Development Roadmap

- [x] Auto-update system
- [x] Donation integration
- [ ] Tor network support
- [ ] JSON output format
- [ ] Rate limiting
- [ ] Search history

## Disclaimer

This tool is intended for **authorized security research only**. Users assume full responsibility for complying with all applicable laws and regulations. The maintainer disclaims any liability for misuse.

---

[Report Issues](https://github.com/byFranke/PastebinSearch/issues) | [View Changelog](CHANGELOG.md) 
