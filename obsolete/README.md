# PastebinSearch Migration Guide - v2.0 to v3.0

## Overview

This guide helps you migrate from PastebinSearch v2.0 (Bash) to v3.0 (Python).

## Key Changes

### **v2.0 (Bash) → v3.0 (Python)**

| Feature | v2.0 (Bash) | v3.0 (Python) |
|---------|-------------|---------------|
| Language | Bash/Shell | Python 3.8+ |
| Interface | Basic CLI | Rich CLI with menus |
| Configuration | Environment variables | JSON config files |
| Search | Simple curl requests | Advanced async search |
| Results | Plain text output | Formatted tables |
| Browser | Manual | Automated with Playwright/Selenium |
| Logging | Basic logs | Comprehensive logging system |
| Installation | Copy script | Full installer with dependencies |

## Migration Steps

### **Step 1: Backup Current Setup**
```bash
# If you have a v2.0 installation, backup your data
cp pastebinsearch.sh pastebinsearch_v2_backup.sh
cp -r results/ results_v2_backup/ 2>/dev/null || true
cp -r logs/ logs_v2_backup/ 2>/dev/null || true
```

### **Step 2: Install v3.0**
```bash
# Navigate to the new PastebinSearch directory
cd PastebinSearch

# Or run the main application directly
python pastebinsearch.py --install
```

### **Step 3: Configuration Migration**

#### **v2.0 Configuration (Environment Variables)**
```bash
# Old way (v2.0)
export PASTEBIN_SEARCH_LIMIT=50
export PASTEBIN_USER_AGENT="Custom-Agent"
export PASTEBIN_RATE_LIMIT=2
```

#### **v3.0 Configuration (JSON)**
```json
{
  "search": {
    "default_limit": 50,
    "user_agent": "Custom-Agent",
    "rate_limit": 2.0
  }
}
```

### **Step 4: Update Scripts and Workflows**

#### **Command Equivalents**

| v2.0 (Bash) | v3.0 (Python) | Description |
|-------------|---------------|-------------|
| `./pastebinsearch.sh -s "term"` | `python pastebinsearch.py --search "term"` | Quick search |
| `./pastebinsearch.sh -l 100` | Use config or interactive mode | Set result limit |
| `./pastebinsearch.sh -o json` | Interactive mode → Export | Output format |
| `./pastebinsearch.sh --config` | `python pastebinsearch.py --config` | Configuration |

#### **Interactive Mode (New in v3.0)**
```bash
# Launch interactive menu system
python pastebinsearch.py

# No equivalent in v2.0 - new feature!
```

## Feature Comparison

### **Retained Features**
Basic search functionality  
Result limiting  
Rate limiting  
User agent customization  
Output to files  

### **Enhanced Features**
🔧 **Search**: More advanced filtering and options  
🔧 **Configuration**: JSON-based with validation  
🔧 **Output**: Rich formatted tables instead of plain text  
🔧 **Error Handling**: Comprehensive error reporting  

### **New Features in v3.0**
**Interactive Menus**: Full menu-driven interface  
**Browser Automation**: Automated browsing with Playwright/Selenium  
**Security Analysis**: Automatic detection of sensitive data  
**Search History**: Complete search history tracking  
**Advanced Logging**: Structured logging system  
**Batch Search**: Process multiple search terms from files  
**Real-time Monitoring**: Monitor pages for changes  
**Professional Installer**: Full installation system  

## Configuration Migration

### **Manual Migration**
1. **Identify your v2.0 settings** (environment variables, custom scripts)
2. **Run v3.0 configuration**: `python pastebinsearch.py --config`
3. **Set equivalent options** in the interactive configuration menu

### **Automated Migration (Future Feature)**
```bash
# Will be available in future updates
python pastebinsearch.py --migrate-from-v2 /path/to/old/config
```

## Data Migration

### **Search Results**
```bash
# v2.0 results were typically in plain text files
# v3.0 can export to multiple formats (JSON, CSV, TXT)

# To convert old results, use the export feature in v3.0
```

### **Logs**
```bash
# v2.0 logs (if any) can be imported manually
# v3.0 has comprehensive logging system

# Copy old logs to new logs directory for reference
cp old_logs/* PastebinSearch/logs/legacy/ 2>/dev/null || true
```

## Learning the New Interface

### **v2.0 Workflow**
```bash
# Old way: Command line arguments
./pastebinsearch.sh -s "password" -l 50 -o json
```

### **v3.0 Workflow Options**

#### **Option 1: Command Line (Similar to v2.0)**
```bash
python pastebinsearch.py --search "password"
```

#### **Option 2: Interactive Mode (Recommended)**
```bash
python pastebinsearch.py
# Then follow the menu system:
# 1 → Search Options → 1 → Enter search term
```

#### **Option 3: Configuration First**
```bash
python pastebinsearch.py --config
# Configure your preferences, then use the tool
```

## Testing Migration

### **Verify Installation**
```bash
# Test that everything works
python pastebinsearch.py --version
python pastebinsearch.py --help
```

### **Compare Results**
```bash
# Test with a known search term from v2.0
# Compare results to ensure consistency
python pastebinsearch.py --search "test term"
```

## Troubleshooting

### **Common Issues**

#### **Python Not Found**
```bash
# Make sure Python 3.8+ is installed
python --version
python3 --version
```

#### **Dependencies Missing**
```bash
# Or install manually
pip install -r requirements.txt
```

#### **Permission Issues**
```bash
# On Unix systems, ensure execute permissions
chmod +x pastebinsearch.py
```

#### **Configuration Issues**
```bash
# Reset to defaults if needed
python pastebinsearch.py --config
# Select: 4 → Reset to Defaults
```

### **Getting Help**
- 🐛 **Issues**: Report on GitHub
- 💬 **Support**: Contact support@byfranke.com

## Migration Complete!

Once migrated, you'll have access to:

### **Immediate Benefits**
- **Better Interface**: Rich, colorful CLI
- **Better Results**: Formatted tables
- **Easy Configuration**: Interactive setup
- **Complete Logging**: Track all activities

### **Advanced Features**
- **Browser Automation**: Automated browsing
- **Security Analysis**: Find exposed credentials
- **Search History**: Track and analyze searches
- **Monitoring**: Real-time change detection

## Checklist

- [ ] Backup v2.0 data (if applicable)
- [ ] Install Python 3.8+
- [ ] Run setup.py or install dependencies
- [ ] Test basic functionality
- [ ] Configure preferences
- [ ] Migrate any custom scripts or workflows
- [ ] Test advanced features
- [ ] Remove old v2.0 installation (optional)

---

**Pro Tip**: Start with interactive mode (`python pastebinsearch.py`) to familiarize yourself with all the new features!

**Remember**: Always use this tool responsibly and ethically for security research only.




