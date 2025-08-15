"""
PastebinSearch Modules Package
Contains all core modules for the PastebinSearch tool
"""

# Version information
__version__ = "3.0.0"
__author__ = "byFranke"
__description__ = "Advanced Security Research Tool for Pastebin"

# Module imports for easy access
try:
    from .config_manager import ConfigManager
    from .ui_manager import UIManager
    from .search_engine import PastebinSearchEngine
    from .browser_manager import BrowserManager
    from .logger import SearchLogger
    from .installer import ToolInstaller
    
    __all__ = [
        'ConfigManager',
        'UIManager', 
        'PastebinSearchEngine',
        'BrowserManager',
        'SearchLogger',
        'ToolInstaller'
    ]
    
except ImportError as e:
    # Handle missing dependencies gracefully
    import warnings
    warnings.warn(f"Some modules could not be imported: {e}", ImportWarning)
    __all__ = []
