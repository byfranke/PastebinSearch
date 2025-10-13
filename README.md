# PastebinSearch v3.1.3

<div align="center">

Advanced Security Research Tool for Pastebin Intelligence Gathering

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)](https://github.com)

Search leaked credentials, API keys, and sensitive information across Pastebin with advanced automation

</div>

---

## Quick Start

### One-Command Installation
```bash
python install_kali.py
```

### Start Searching
```bash

# Interactive mode with full interface
pastebinsearch

# Test connectivity and SSL
pastebinsearch --diagnose

# Show help and all options
pastebinsearch --help

# Search for leaked passwords
pastebinsearch --search "password"

# Find exposed API keys
pastebinsearch --search "api key"

# Manual browser automation
pastebinsearch --search "database"

# Quick password search
pastebinsearch --search "password"

# Database credentials
pastebinsearch --search "database password mysql"

# API keys and tokens
pastebinsearch --search "api_key OR token OR secret"

# Configuration files
pastebinsearch --search "config database host user"
```

The tool is ready for ethical security research.

---

## Features

<table>
<tr>
<td width="50%">

### Multi-Engine Search
- **DuckDuckGo HTML** - Primary search method
- **Google Site Search** - Backup method  
- **Bing Integration** - Additional coverage
- **Direct Pastebin** - Archive & trending
- **Smart Fallbacks** - Never miss results

### Browser Automation
- **Selenium Integration** - Real browser automation
- **Anti-Bot Bypass** - Advanced evasion techniques
- **Manual Mode** - Human-like navigation
- **WebDriver Manager** - Automatic driver setup
- **Multi-Browser Support** - Chrome, Firefox, Edge

</td>
<td width="50%">

### Security & Privacy
- **SSL/TLS Hardening** - Multiple certificate strategies
- **Proxy Support** - Route through proxies
- **User-Agent Rotation** - Avoid detection
- **Rate Limiting** - Respectful scraping
- **Session Management** - Persistent connections

### Rich Interface
- **Beautiful CLI** - Rich terminal UI with colors
- **Progress Tracking** - Real-time search progress
- **Interactive Menus** - User-friendly navigation
- **Search History** - Track previous searches
- **Export Results** - JSON, CSV, TXT formats

</td>
</tr>
</table>

---

What it does:
- **Auto-detects** your operating system and Python environment
- **Installs dependencies** including brotli, selenium, and webdrivers  
- **Creates shortcuts** and system integration
- **Tests installation** to ensure everything works
- **Handles edge cases** like externally-managed Python environments


### Windows Specific
```bash
# Standard installation
python install_universal.py

# Manual PATH setup if needed
# Add C:\Users\[USER]\AppData\Local\Programs\PastebinSearch to PATH
```

### Manual Installation
```bash
# Install dependencies manually
pip install rich aiohttp beautifulsoup4 lxml requests python-dotenv brotli selenium webdriver-manager asyncio-throttle loguru cryptography pydantic colorama

# Run directly
python pastebinsearch.py
```

---

### Search Strategies

#### High Success Rate (Automated)
- `password` - Login credentials
- `database` - Database dumps
- `api` - API keys and endpoints  
- `config` - Configuration files
- `mysql` - Database credentials
- `mongodb` - NoSQL databases
- `postgresql` - PostgreSQL credentials

#### May Require Manual Mode
- `credit card` - Financial data
- `social security` - Personal identifiers
- `bank account` - Banking information
- `medical records` - Healthcare data

---

## Project Structure

```
PastebinSearch/
├── install.py             # Universal installer (START HERE)
├── pastebinsearch.py      # Main application
├── README.md              # This documentation
├── requirements.txt       # Python dependencies  
├── LICENSE                # License
├── modules/               # Core functionality
│   ├── config_manager.py  # Configuration management
│   ├── ui_manager.py      # User interface components
│   ├── search_engine.py   # Search algorithms
│   ├── browser_manager.py # Browser automation
│   ├── logger.py          # Logging system
│   └── installer.py       # Installation utilities
├── config/                # Configuration files
│   └── default_config.json
├── logs/                  # Application logs
└── obsolete/              # Legacy files and documentation
  ├── v1.0               # Legacy pastebinsearch v1.0  
  ├── v2.0               # Legacy pastebinsearch v2.0
  ├── README.md          # Guide v2.0 to v3.0
  ├── install_helper.py  # Helper install
  └── install_kali.py    # Alternative installers
```

---

## Common Issues & Solutions


### "No results found"
```bash
# Try manual mode to bypass anti-bot measures
pastebinsearch --manual --search "your_term"
```

### "Command not found: pastebinsearch"
```bash
# Windows: Add to PATH or use full path
C:\Users\[USER]\AppData\Local\Programs\PastebinSearch\pastebinsearch.bat

# Linux/macOS: Restart terminal or source bashrc
source ~/.bashrc
```

---

## Legal & Ethical Guidelines

### Authorized Use Cases
- **Security Research** - Finding your own organization's data breaches
- **Penetration Testing** - Authorized testing with proper agreements
- **Educational Purposes** - Learning about information security
- **Personal Monitoring** - Checking if your own data was leaked
- **Bug Bounty Programs** - Responsible disclosure programs

### Prohibited Activities
- **Unauthorized Access** - Accessing systems without permission
- **Identity Theft** - Using found credentials maliciously
- **Financial Fraud** - Exploiting financial information
- **Privacy Violations** - Stalking or harassment
- **Commercial Exploitation** - Selling or distributing found data

### Legal Compliance
- **Know Your Local Laws** - Information security laws vary by jurisdiction
- **Obtain Proper Authorization** - Get written permission for testing
- **Responsible Disclosure** - Report vulnerabilities responsibly
- **Data Protection** - Handle sensitive data according to regulations (GDPR, CCPA, etc.)

By using PastebinSearch, you agree to use it responsibly and in compliance with all applicable laws and regulations.

---

## Advanced Configuration

### Configuration Options
```json
{
  "search": {
    "timeout": 30,
    "max_results": 50,
    "rate_limit": 2.0,
    "user_agent": "PastebinSearch/3.0",
    "proxy": {
      "enabled": false,
      "http": "http://proxy:8080",
      "https": "https://proxy:8080"
    }
  },
  "advanced": {
    "ssl_verify": false,
    "follow_redirects": true,
    "retry_attempts": 3
  }
}
```

### Environment Variables
```bash
# Proxy configuration
export HTTP_PROXY="http://proxy:8080"
export HTTPS_PROXY="https://proxy:8080"

# Debug mode
export PASTEBINSEARCH_DEBUG=1

# Custom config file
export PASTEBINSEARCH_CONFIG="/path/to/config.json"
```

---

## Contributing

We welcome contributions from the security research community!


### Contribution Guidelines
1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write** tests for your changes
4. **Ensure** all tests pass (`pytest`)
5. **Format** your code (`black .`)
6. **Commit** your changes (`git commit -m 'Add amazing feature'`)
7. **Push** to the branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Bug Reports
Please use the [GitHub Issues](https://github.com/byFranke/PastebinSearch/issues) page to report bugs. Include:
- Operating system and version
- Python version
- Complete error message
- Steps to reproduce
- Expected vs actual behavior

---

## Performance & Monitoring

### Search Methods Performance
| Method | Success Rate | Speed | Anti-Bot Resistance |
|--------|-------------|--------|-------------------|
| DuckDuckGo HTML | 95% | Fast | High |
| Google Site Search | 70% | Medium | Medium |
| Bing Integration | 60% | Fast | Medium |
| Manual Browser | 99% | Slow | Highest |
| Direct Pastebin | 10% | Fast | Low |

### Search Statistics
- **Average Search Time**: 15-30 seconds
- **Typical Results**: 10-50 pastes per search
- **Success Rate**: 85%+ with automatic methods
- **Memory Usage**: 50-100MB during search
- **Network Usage**: 5-20MB per search

---

## Acknowledgments

### Contributors
- **byFranke** - Original author and maintainer
- **Security Community** - Bug reports, feature requests, and testing

### Technologies Used
- **Python** - Core programming language
- **aiohttp** - Async HTTP client
- **Rich** - Terminal UI framework
- **Selenium** - Browser automation
- **BeautifulSoup** - HTML parsing
- **Loguru** - Advanced logging

---

## Support & Contact

### Get Help
- Website: [byfranke.com](https://byfranke.com)
- Issues: [GitHub Issues](https://github.com/byFranke/PastebinSearch/issues)
- Contact: Via website contact form
- Feature Requests: Open a GitHub issue with the "enhancement" label

### Stay Updated
- Star this repository to get notified of updates
- Watch for new releases and security updates
- Check for updates: `pastebinsearch --update`

---



## Donation Support

This tool is maintained through community support. Help keep it active:

[![Donate](https://img.shields.io/badge/Support-Development-blue?style=for-the-badge&logo=github)](https://buy.byfranke.com/b/8wM03kb3u7THeIgaEE)








