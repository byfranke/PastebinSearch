"""
Configuration Manager for PastebinSearch Tool
Handles configuration loading, saving, and management
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.console import Console

class ConfigManager:
    """Manages tool configuration"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_file = self.config_dir / "config.json"
        self.default_config = self.get_default_config()
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "general": {
                "version": "3.0.0",
                "auto_update": True,
                "debug_mode": False,
                "log_level": "INFO"
            },
            "search": {
                "default_limit": 50,
                "max_results": 200,
                "timeout": 30,
                "rate_limit": 3.0,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "proxy": {
                    "enabled": False,
                    "http_proxy": "",
                    "https_proxy": ""
                }
            },
            "browser": {
                "headless": True,
                "browser_type": "chromium",
                "window_size": "1920x1080",
                "timeout": 30,
                "auto_download": True,
                "download_path": "./downloads"
            },
            "output": {
                "format": "table",
                "save_results": True,
                "results_path": "./results",
                "export_formats": ["json", "csv", "txt"],
                "timestamp_format": "%Y-%m-%d %H:%M:%S"
            },
            "alerts": {
                "enabled": False,
                "email": {
                    "enabled": False,
                    "smtp_server": "",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipients": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "secret": ""
                }
            },
            "advanced": {
                "concurrent_searches": 3,
                "retry_attempts": 3,
                "cache_enabled": True,
                "cache_duration": 3600,
                "ssl_verify": False
            }
        }
    
    async def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            await self.save_config(self.default_config)
            return self.default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Merge with default config to ensure all keys exist
            return self.merge_configs(self.default_config, config)
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Error loading config: {e}")
            return self.default_config
    
    async def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"❌ Error saving config: {e}")
            return False
    
    def merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with default config"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    async def edit_config_interactive(self, console: Console):
        """Interactive configuration editor"""
        config = await self.load_config()
        
        console.print("\n[bold cyan]🔧 Configuration Editor[/bold cyan]")
        
        while True:
            self.show_config_menu(console, config)
            
            choice = Prompt.ask(
                "[cyan]Select section to edit (0 to save & exit)",
                choices=["0", "1", "2", "3", "4", "5", "6"],
                default="0"
            )
            
            if choice == "0":
                if await self.save_config(config):
                    console.print("[green]✅ Configuration saved successfully![/green]")
                else:
                    console.print("[red]❌ Error saving configuration[/red]")
                break
            elif choice == "1":
                await self.edit_general_config(console, config)
            elif choice == "2":
                await self.edit_search_config(console, config)
            elif choice == "3":
                await self.edit_browser_config(console, config)
            elif choice == "4":
                await self.edit_output_config(console, config)
            elif choice == "5":
                await self.edit_alerts_config(console, config)
            elif choice == "6":
                await self.edit_advanced_config(console, config)
    
    def show_config_menu(self, console: Console, config: Dict[str, Any]):
        """Show configuration menu"""
        menu_text = f"""
[yellow]Current Configuration Sections:[/yellow]

[cyan]1.[/cyan] General Settings
   • Version: {config['general']['version']}
   • Auto Update: {config['general']['auto_update']}
   • Debug Mode: {config['general']['debug_mode']}

[cyan]2.[/cyan] Search Settings
   • Default Limit: {config['search']['default_limit']}
   • Timeout: {config['search']['timeout']}s
   • Rate Limit: {config['search']['rate_limit']}s

[cyan]3.[/cyan] Browser Settings
   • Headless: {config['browser']['headless']}
   • Browser Type: {config['browser']['browser_type']}
   • Window Size: {config['browser']['window_size']}

[cyan]4.[/cyan] Output Settings
   • Format: {config['output']['format']}
   • Save Results: {config['output']['save_results']}
   • Results Path: {config['output']['results_path']}

[cyan]5.[/cyan] Alert Settings
   • Enabled: {config['alerts']['enabled']}
   • Email Alerts: {config['alerts']['email']['enabled']}
   • Webhooks: {config['alerts']['webhook']['enabled']}

[cyan]6.[/cyan] Advanced Settings
   • Concurrent Searches: {config['advanced']['concurrent_searches']}
   • Retry Attempts: {config['advanced']['retry_attempts']}
   • Cache Enabled: {config['advanced']['cache_enabled']}

[cyan]0.[/cyan] Save & Exit
        """
        console.print(Panel(menu_text, title="Configuration Menu", border_style="blue"))
    
    async def edit_general_config(self, console: Console, config: Dict[str, Any]):
        """Edit general configuration"""
        console.print("\n[bold yellow]📋 General Settings[/bold yellow]")
        
        config['general']['auto_update'] = Confirm.ask(
            "Enable auto update?", 
            default=config['general']['auto_update']
        )
        
        config['general']['debug_mode'] = Confirm.ask(
            "Enable debug mode?", 
            default=config['general']['debug_mode']
        )
        
        log_level = Prompt.ask(
            "Log level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default=config['general']['log_level']
        )
        config['general']['log_level'] = log_level
    
    async def edit_search_config(self, console: Console, config: Dict[str, Any]):
        """Edit search configuration"""
        console.print("\n[bold yellow]🔍 Search Settings[/bold yellow]")
        
        config['search']['default_limit'] = IntPrompt.ask(
            "Default result limit",
            default=config['search']['default_limit']
        )
        
        config['search']['max_results'] = IntPrompt.ask(
            "Maximum results",
            default=config['search']['max_results']
        )
        
        config['search']['timeout'] = IntPrompt.ask(
            "Request timeout (seconds)",
            default=config['search']['timeout']
        )
        
        config['search']['rate_limit'] = float(Prompt.ask(
            "Rate limit (seconds between requests)",
            default=str(config['search']['rate_limit'])
        ))
        
        # Proxy settings
        console.print("\n[cyan]Proxy Settings:[/cyan]")
        config['search']['proxy']['enabled'] = Confirm.ask(
            "Use proxy?",
            default=config['search']['proxy']['enabled']
        )
        
        if config['search']['proxy']['enabled']:
            config['search']['proxy']['http_proxy'] = Prompt.ask(
                "HTTP proxy URL",
                default=config['search']['proxy']['http_proxy']
            )
            config['search']['proxy']['https_proxy'] = Prompt.ask(
                "HTTPS proxy URL",
                default=config['search']['proxy']['https_proxy']
            )
    
    async def edit_browser_config(self, console: Console, config: Dict[str, Any]):
        """Edit browser configuration"""
        console.print("\n[bold yellow]🌐 Browser Settings[/bold yellow]")
        
        config['browser']['headless'] = Confirm.ask(
            "Run browser in headless mode?",
            default=config['browser']['headless']
        )
        
        browser_type = Prompt.ask(
            "Browser type",
            choices=["chromium", "firefox", "webkit"],
            default=config['browser']['browser_type']
        )
        config['browser']['browser_type'] = browser_type
        
        config['browser']['window_size'] = Prompt.ask(
            "Window size (WxH)",
            default=config['browser']['window_size']
        )
        
        config['browser']['timeout'] = IntPrompt.ask(
            "Page timeout (seconds)",
            default=config['browser']['timeout']
        )
        
        config['browser']['auto_download'] = Confirm.ask(
            "Auto download files?",
            default=config['browser']['auto_download']
        )
        
        config['browser']['download_path'] = Prompt.ask(
            "Download path",
            default=config['browser']['download_path']
        )
    
    async def edit_output_config(self, console: Console, config: Dict[str, Any]):
        """Edit output configuration"""
        console.print("\n[bold yellow]📄 Output Settings[/bold yellow]")
        
        output_format = Prompt.ask(
            "Display format",
            choices=["table", "json", "simple"],
            default=config['output']['format']
        )
        config['output']['format'] = output_format
        
        config['output']['save_results'] = Confirm.ask(
            "Save results to files?",
            default=config['output']['save_results']
        )
        
        if config['output']['save_results']:
            config['output']['results_path'] = Prompt.ask(
                "Results directory",
                default=config['output']['results_path']
            )
        
        config['output']['timestamp_format'] = Prompt.ask(
            "Timestamp format",
            default=config['output']['timestamp_format']
        )
    
    async def edit_alerts_config(self, console: Console, config: Dict[str, Any]):
        """Edit alerts configuration"""
        console.print("\n[bold yellow]🔔 Alert Settings[/bold yellow]")
        
        config['alerts']['enabled'] = Confirm.ask(
            "Enable alerts?",
            default=config['alerts']['enabled']
        )
        
        if config['alerts']['enabled']:
            # Email alerts
            console.print("\n[cyan]Email Alerts:[/cyan]")
            config['alerts']['email']['enabled'] = Confirm.ask(
                "Enable email alerts?",
                default=config['alerts']['email']['enabled']
            )
            
            if config['alerts']['email']['enabled']:
                config['alerts']['email']['smtp_server'] = Prompt.ask(
                    "SMTP server",
                    default=config['alerts']['email']['smtp_server']
                )
                config['alerts']['email']['smtp_port'] = IntPrompt.ask(
                    "SMTP port",
                    default=config['alerts']['email']['smtp_port']
                )
                config['alerts']['email']['username'] = Prompt.ask(
                    "Username",
                    default=config['alerts']['email']['username']
                )
                
                if Confirm.ask("Update password?"):
                    config['alerts']['email']['password'] = Prompt.ask(
                        "Password",
                        password=True
                    )
            
            # Webhook alerts
            console.print("\n[cyan]Webhook Alerts:[/cyan]")
            config['alerts']['webhook']['enabled'] = Confirm.ask(
                "Enable webhook alerts?",
                default=config['alerts']['webhook']['enabled']
            )
            
            if config['alerts']['webhook']['enabled']:
                config['alerts']['webhook']['url'] = Prompt.ask(
                    "Webhook URL",
                    default=config['alerts']['webhook']['url']
                )
                config['alerts']['webhook']['secret'] = Prompt.ask(
                    "Webhook secret",
                    default=config['alerts']['webhook']['secret']
                )
    
    async def edit_advanced_config(self, console: Console, config: Dict[str, Any]):
        """Edit advanced configuration"""
        console.print("\n[bold yellow]⚡ Advanced Settings[/bold yellow]")
        
        config['advanced']['concurrent_searches'] = IntPrompt.ask(
            "Concurrent searches",
            default=config['advanced']['concurrent_searches']
        )
        
        config['advanced']['retry_attempts'] = IntPrompt.ask(
            "Retry attempts",
            default=config['advanced']['retry_attempts']
        )
        
        config['advanced']['cache_enabled'] = Confirm.ask(
            "Enable caching?",
            default=config['advanced']['cache_enabled']
        )
        
        if config['advanced']['cache_enabled']:
            config['advanced']['cache_duration'] = IntPrompt.ask(
                "Cache duration (seconds)",
                default=config['advanced']['cache_duration']
            )
        
        config['advanced']['ssl_verify'] = Confirm.ask(
            "Verify SSL certificates?",
            default=config['advanced']['ssl_verify']
        )
    
    async def export_config(self):
        """Export configuration to file"""
        config = await self.load_config()
        export_path = Path("config_export.json")
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"✅ Configuration exported to {export_path}")
        except IOError as e:
            print(f"❌ Export failed: {e}")
    
    async def import_config(self):
        """Import configuration from file"""
        from rich.prompt import Prompt
        
        file_path = Prompt.ask("Enter config file path")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            if await self.save_config(imported_config):
                print("✅ Configuration imported successfully!")
            else:
                print("❌ Import failed - couldn't save configuration")
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"❌ Import failed: {e}")
    
    async def reset_config(self):
        """Reset configuration to defaults"""
        from rich.prompt import Confirm
        
        if Confirm.ask("⚠️  Reset all settings to default?"):
            if await self.save_config(self.default_config):
                print("✅ Configuration reset to defaults")
            else:
                print("❌ Reset failed")
    
    def get_config_value(self, key_path: str, config: Optional[Dict] = None) -> Any:
        """Get a configuration value using dot notation"""
        if config is None:
            import asyncio
            config = asyncio.run(self.load_config())
        
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    async def set_config_value(self, key_path: str, value: Any):
        """Set a configuration value using dot notation"""
        config = await self.load_config()
        keys = key_path.split('.')
        
        # Navigate to the parent dictionary
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        # Save the configuration
        await self.save_config(config)
