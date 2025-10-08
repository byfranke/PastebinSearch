"""
Installer and Uninstaller for PastebinSearch Tool
Handles installation, dependency management, and system setup
"""

import os
import sys
import subprocess
import shutil
import json
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import urllib.request

class ToolInstaller:
    """Handles installation and uninstallation of PastebinSearch"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.tool_name = "PastebinSearch"
        self.version = "3.1.3"
        self.python_min_version = (3, 8)
        
        # Installation paths
        if self.system == "windows":
            self.install_base = Path.home() / "AppData" / "Local" / self.tool_name
            self.bin_path = self.install_base / "bin"
            self.scripts_path = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"
        else:
            self.install_base = Path.home() / ".local" / "share" / self.tool_name.lower()
            self.bin_path = Path.home() / ".local" / "bin"
            self.scripts_path = self.bin_path
        
        # Configuration
        self.config_path = Path.home() / f".{self.tool_name.lower()}"
        
        # Requirements
        self.core_requirements = [
            "rich>=13.7.0",
            "aiohttp>=3.9.0",
            "beautifulsoup4>=4.12.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "asyncio-throttle>=1.0.2",
            "loguru>=0.7.2",
            "pydantic>=2.4.0",
            "colorama>=0.4.6"
        ]
        
        self.optional_requirements = [
            ("playwright>=1.35.0", "Browser automation with Playwright"),
            ("selenium>=4.10.0", "Browser automation with Selenium"),
            ("pandas>=1.5.0", "Advanced data export features"),
            ("cryptography>=3.4.0", "Enhanced security features")
        ]
    
    def check_system_requirements(self) -> bool:
        """Check if system meets requirements"""
        print("Checking system requirements...")
        
        # Check Python version
        current_version = sys.version_info[:2]
        if current_version < self.python_min_version:
            print(f"[ERROR] Python {self.python_min_version[0]}.{self.python_min_version[1]}+ required. Current: {current_version[0]}.{current_version[1]}")
            return False
        
        print(f"Python {current_version[0]}.{current_version[1]} - OK")
        
        # Check pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print("pip - OK")
        except subprocess.CalledProcessError:
            print("[ERROR] pip not found or not working")
            return False
        
        # Check internet connection for package installation
        try:
            urllib.request.urlopen('https://pypi.org', timeout=5)
            print("Internet connection - OK")
        except:
            print("[WARNING] Limited internet connection - some features may not work")
        
        # Check available disk space (estimate 100MB needed)
        free_space = shutil.disk_usage(Path.home()).free
        required_space = 100 * 1024 * 1024  # 100MB
        
        if free_space < required_space:
            print(f"[ERROR] Insufficient disk space. Required: 100MB, Available: {free_space // (1024*1024)}MB")
            return False
        
        print("Disk space - OK")
        return True
