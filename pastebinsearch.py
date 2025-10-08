#!/usr/bin/env python3
"""
PastebinSearch v3.1.3 - Advanced Security Research Tool
Author: byFranke
Description: Modern Python-based tool for searching Pastebin with enhanced UI and automation
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Rich imports for enhanced CLI
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.live import Live
from rich import box
from rich.layout import Layout
from rich.align import Align

# Local modules
from modules.search_engine import PastebinSearchEngine
from modules.browser_manager import BrowserManager
from modules.ui_manager import UIManager
from modules.config_manager import ConfigManager
from modules.logger import SearchLogger
from modules.installer import ToolInstaller

class PastebinSearchTool:
    """Main class for the PastebinSearch tool"""
    
    def __init__(self):
        """Initialize the tool"""
        self.console = Console()
        self.config_manager = ConfigManager()
        self.ui_manager = UIManager(self.console)
        self.logger = SearchLogger()
        self.search_engine = None
        self.browser_manager = None
        self.version = "3.1.0"
        self.banner_shown = False
        
    def show_banner(self):
        """Display the tool banner"""
        if not self.banner_shown:
            self.ui_manager.show_banner(self.version)
            self.banner_shown = True
    
    def show_help(self):
        """Display help information"""
        help_text = f"""
[bold cyan]PastebinSearch v{self.version} - Usage Guide[/bold cyan]

[yellow]COMMAND LINE OPTIONS:[/yellow]
  --search <term>     : Automatic search (tries 5 methods)
  --manual <term>     : Force manual browser search 
  --config           : Configuration menu
  --diagnose         : Test connectivity and diagnose issues
  --install          : Install the tool
  --uninstall        : Uninstall the tool
  --version          : Show version info
  --help             : Show this help

[yellow]SEARCH MODES:[/yellow]
  [bold]Automatic Mode[/bold] (--search):
     • Tries DuckDuckGo, Google, Bing, Pastebin Archive
     • Works for most terms: password, database, api, config
     • Fast and convenient

  [bold]Manual Mode[/bold] (--manual):
     • Opens browser tabs for manual searching
     • Better for blocked/sensitive terms
     • More reliable against anti-bot measures

[yellow]EXAMPLES:[/yellow]
  python pastebinsearch.py --search "database leak"
  python pastebinsearch.py --manual "credit card"
  python pastebinsearch.py --diagnose
  python pastebinsearch.py

[yellow]WHEN TO USE MANUAL MODE:[/yellow]
  • Sensitive terms (credit card, ssn, bank)
  • No automatic results found
  • Anti-bot blocking detected
  • Need maximum search coverage
        """
        self.console.print(Panel(help_text, title="Help", border_style="green"))
    
    async def quick_search(self, search_term: str):
        """Perform a quick search from command line"""
        self.show_banner()
        
        if not self.search_engine:
            config = await self.config_manager.load_config()
            self.search_engine = PastebinSearchEngine(config)
        
        self.console.print(f"\n[green]Searching for:[/green] {search_term}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task("Searching Pastebin...", total=None)
            
            try:
                results = await self.search_engine.search(search_term)
                progress.update(task, completed=100)
                
                if results:
                    self.ui_manager.display_results(results, search_term)
                    self.logger.log_search(search_term, len(results))
                else:
                    self.console.print("[yellow]No results found[/yellow]")
                    
            except Exception as e:
                progress.remove_task(task)
                error_msg = str(e)
                
                # Show specific error guidance
                if "SSL Certificate Error" in error_msg:
                    self.ui_manager.show_error_message(
                        "SSL Certificate Problem",
                        "There's an issue with SSL certificate verification.",
                        "Run 'python pastebinsearch.py --diagnose' to test connectivity and get fix suggestions."
                    )
                elif "Connection Error" in error_msg:
                    self.ui_manager.show_error_message(
                        "Connection Problem",
                        "Cannot connect to Pastebin servers.",
                        "Check your internet connection and firewall settings. Run '--diagnose' for more info."
                    )
                else:
                    self.console.print(f"[red]Search error: {error_msg}[/red]")
                
                self.logger.log_error(f"Search error: {error_msg}")
            
            finally:
                # Clean up the session
                if self.search_engine:
                    await self.search_engine.close_session()
    
    async def manual_search(self, search_term: str):
        """Force manual browser search"""
        self.show_banner()
        
        if not self.search_engine:
            config = await self.config_manager.load_config()
            self.search_engine = PastebinSearchEngine(config)
        
        self.console.print(f"\n[green]Manual Search Mode for:[/green] {search_term}")
        
        try:
            # Force manual search directly
            results = await self.search_engine._open_manual_search(search_term)
            
            if results:
                self.ui_manager.display_results(results, search_term)
                self.logger.log_search(f"{search_term} (manual)", len(results))
            else:
                self.console.print("[yellow]Manual search completed[/yellow]")
                
        except Exception as e:
            error_msg = str(e)
            self.console.print(f"[red]Manual search error: {error_msg}[/red]")
            self.logger.log_error(f"Manual search error: {error_msg}")
        
        finally:
            # Clean up the session
            if self.search_engine:
                await self.search_engine.close_session()
    
    async def diagnose_connectivity(self):
        """Diagnose connectivity issues"""
        self.show_banner()
        
        self.console.print("[cyan]Running connectivity diagnostics...[/cyan]\n")
        
        if not self.search_engine:
            config = await self.config_manager.load_config()
            self.search_engine = PastebinSearchEngine(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task("Testing connection...", total=None)
            
            try:
                results = await self.search_engine.test_connectivity()
                progress.remove_task(task)
                
                # Display results
                status_color = "green" if results['pastebin_reachable'] else "red"
                ssl_color = "green" if results['ssl_working'] else "yellow"
                
                self.console.print(f"[{status_color}]Pastebin Reachable:[/{status_color}] {results['pastebin_reachable']}")
                self.console.print(f"[{ssl_color}]SSL Working:[/{ssl_color}] {results['ssl_working']}")
                
                if results['response_time'] > 0:
                    self.console.print(f"[blue]Response Time:[/blue] {results['response_time']:.2f}s")
                
                if results['error_details']:
                    self.ui_manager.show_error_message(
                        "Connection Issue Detected",
                        results['error_details'],
                        results['suggested_fix']
                    )
                elif results['pastebin_reachable']:
                    self.ui_manager.show_success_message(
                        "Connection Successful",
                        "All connectivity tests passed! PastebinSearch should work normally."
                    )
                
            except Exception as e:
                progress.remove_task(task)
                self.ui_manager.show_error_message(
                    "Diagnostic Failed",
                    f"Could not complete connectivity test: {str(e)}",
                    "Check your internet connection and try again."
                )
                
            finally:
                # Clean up the session
                if self.search_engine:
                    await self.search_engine.close_session()
    
    async def interactive_mode(self):
        """Run the tool in interactive mode"""
        self.show_banner()
        
        # Initialize components
        config = await self.config_manager.load_config()
        self.search_engine = PastebinSearchEngine(config)
        self.browser_manager = BrowserManager()
        
        while True:
            try:
                choice = self.ui_manager.show_main_menu()
                
                if choice == "1":
                    await self.handle_search_menu()
                elif choice == "2":
                    await self.handle_browser_menu()
                elif choice == "3":
                    await self.handle_config_menu()
                elif choice == "4":
                    await self.handle_results_menu()
                elif choice == "5":
                    self.handle_logs_menu()
                elif choice == "6":
                    self.show_about()
                elif choice == "0":
                    if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
                        self.console.print("[green]Goodbye![/green]")
                        break
                else:
                    self.console.print("[red]Invalid option. Please try again.[/red]")
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Operation cancelled[/yellow]")
                if Confirm.ask("[yellow]Exit the tool?[/yellow]"):
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
                self.logger.log_error(f"Interactive mode error: {str(e)}")
    
    async def handle_search_menu(self):
        """Handle the search submenu"""
        while True:
            choice = self.ui_manager.show_search_menu()
            
            if choice == "1":
                search_term = Prompt.ask("[cyan]Enter search term")
                if search_term:
                    await self.quick_search(search_term)
            elif choice == "2":
                await self.advanced_search()
            elif choice == "3":
                await self.batch_search()
            elif choice == "4":
                self.show_search_history()
            elif choice == "0":
                break
    
    async def handle_browser_menu(self):
        """Handle the browser automation submenu"""
        while True:
            choice = self.ui_manager.show_browser_menu()
            
            if choice == "1":
                await self.browser_manager.start_browser()
            elif choice == "2":
                await self.browser_manager.auto_navigate()
            elif choice == "3":
                await self.browser_manager.monitor_changes()
            elif choice == "4":
                await self.browser_manager.stop_browser()
            elif choice == "0":
                break
    
    async def handle_config_menu(self):
        """Handle the configuration submenu"""
        while True:
            choice = self.ui_manager.show_config_menu()
            
            if choice == "1":
                await self.config_manager.edit_config_interactive(self.console)
            elif choice == "2":
                await self.config_manager.export_config()
            elif choice == "3":
                await self.config_manager.import_config()
            elif choice == "4":
                await self.config_manager.reset_config()
            elif choice == "0":
                break
    
    async def handle_results_menu(self):
        """Handle the results management submenu"""
        while True:
            choice = self.ui_manager.show_results_menu()
            
            if choice == "1":
                self.show_recent_results()
            elif choice == "2":
                self.export_results()
            elif choice == "3":
                self.clear_results()
            elif choice == "0":
                break
    
    def handle_logs_menu(self):
        """Handle the logs submenu"""
        while True:
            choice = self.ui_manager.show_logs_menu()
            
            if choice == "1":
                self.logger.show_recent_logs(self.console)
            elif choice == "2":
                self.logger.show_error_logs(self.console)
            elif choice == "3":
                self.logger.clear_logs()
            elif choice == "4":
                self.logger.export_logs()
            elif choice == "0":
                break
    
    async def advanced_search(self):
        """Handle advanced search with filters"""
        self.console.print("\n[bold cyan]Advanced Search Configuration[/bold cyan]")
        
        search_term = Prompt.ask("[cyan]Search term")
        date_range = Prompt.ask("[cyan]Date range (days)", default="7")
        result_limit = Prompt.ask("[cyan]Max results", default="50")
        
        filters = {
            'date_range': int(date_range),
            'limit': int(result_limit),
            'advanced': True
        }
        
        await self.perform_search_with_filters(search_term, filters)
    
    async def batch_search(self):
        """Handle batch search from file"""
        file_path = Prompt.ask("[cyan]Enter file path with search terms")
        
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                terms = [line.strip() for line in f if line.strip()]
            
            self.console.print(f"[green]Found {len(terms)} search terms[/green]")
            
            for i, term in enumerate(terms, 1):
                self.console.print(f"\n[yellow]Search {i}/{len(terms)}: {term}[/yellow]")
                await self.quick_search(term)
                await asyncio.sleep(1)  # Rate limiting
        else:
            self.console.print("[red]File not found[/red]")
    
    async def perform_search_with_filters(self, search_term: str, filters: Dict):
        """Perform search with advanced filters"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            console=self.console
        ) as progress:
            task = progress.add_task("Advanced search in progress...", total=None)
            
            try:
                results = await self.search_engine.advanced_search(search_term, filters)
                progress.update(task, completed=100)
                
                if results:
                    self.ui_manager.display_results(results, search_term)
                    self.logger.log_search(f"{search_term} (advanced)", len(results))
                else:
                    self.console.print("[yellow]No results found with current filters[/yellow]")
                    
            except Exception as e:
                self.console.print(f"[red]Search error: {str(e)}[/red]")
                self.logger.log_error(f"Advanced search error: {str(e)}")
    
    def show_search_history(self):
        """Display search history"""
        history = self.logger.get_search_history()
        
        if history:
            table = Table(title="Search History", box=box.ROUNDED)
            table.add_column("Date", style="cyan")
            table.add_column("Search Term", style="yellow")
            table.add_column("Results", style="green")
            
            for entry in history[-20:]:  # Show last 20 searches
                table.add_row(
                    entry['date'],
                    entry['term'],
                    str(entry['results'])
                )
            
            self.console.print(table)
        else:
            self.console.print("[yellow]No search history found[/yellow]")
    
    def show_recent_results(self):
        """Display recent search results"""
        self.console.print("[cyan]Recent Results Feature - Coming Soon[/cyan]")
    
    def export_results(self):
        """Export results to file"""
        self.console.print("[cyan]Export Feature - Coming Soon[/cyan]")
    
    def clear_results(self):
        """Clear stored results"""
        if Confirm.ask("[yellow]Clear all stored results?[/yellow]"):
            self.console.print("[green]Results cleared[/green]")
    
    def show_about(self):
        """Show about information"""
        about_text = f"""
[bold cyan]PastebinSearch v{self.version}[/bold cyan]

[yellow]Advanced Security Research Tool[/yellow]

[green]Features:[/green]
• Interactive CLI with rich interface
• Advanced search capabilities
• Browser automation
• Results management
• Configuration system
• Comprehensive logging

[green]Author:[/green] byFranke
[green]License:[/green] MIT
[green]Repository:[/green] github.com/byfranke/pastebinsearch

[red]Legal Notice:[/red]
This tool is for legitimate security research only.
Always respect robots.txt and terms of service.
        """
        self.console.print(Panel(about_text, title="About", border_style="blue"))

    def show_donation_info(self):
        """Show donation information (backward compatibility with v2.0)"""
        donation_text = """
[yellow]Support PastebinSearch Development[/yellow]

This tool is maintained by byFranke Universe. If you find it useful,
please consider supporting its development through donations.

[bold green]Donation URL:[/bold green] https://donate.stripe.com/28o8zQ2wY3Dr57G001
[bold green]BTC:[/bold green] bc1qk5f0rmpaecwnx334k4w0ek80f72ffsgsuat3nt

[bold]Your support helps:[/bold]
• Maintain and improve the tool
• Add new security features  
• Provide community support
• Keep the tool free and open source

[italic]Thank you for using PastebinSearch responsibly![/italic]
        """
        self.console.print(Panel(donation_text, title="Donate", border_style="yellow"))
        
        # Ask if user wants to open donation link
        from rich.prompt import Confirm
        if Confirm.ask("Open donation link in browser?", default=False):
            import webbrowser
            try:
                webbrowser.open("https://donate.stripe.com/28o8zQ2wY3Dr57G001")
                self.console.print("[green]Donation page opened in browser[/green]")
            except Exception:
                self.console.print("[yellow]Please visit: https://donate.stripe.com/28o8zQ2wY3Dr57G001[/yellow]")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PastebinSearch v3.0 - Advanced Security Research Tool"
    )
    parser.add_argument("--search", help="Quick search term")
    parser.add_argument("--manual", help="Force manual browser search for term")
    parser.add_argument("--config", action="store_true", help="Configuration menu")
    parser.add_argument("--install", action="store_true", help="Install the tool")
    parser.add_argument("--test-deps", action="store_true", help="Test optional dependencies installation")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the tool")
    parser.add_argument("--update", "-u", action="store_true", help="Update to latest version")
    parser.add_argument("--donate", "-d", action="store_true", help="Show donation information")
    parser.add_argument("--diagnose", action="store_true", help="Run connectivity diagnostics")
    parser.add_argument("--version", "-v", action="store_true", help="Show version")
    
    args = parser.parse_args()
    
    # Initialize the tool
    tool = PastebinSearchTool()
    
    try:
        if args.version:
            tool.console.print(f"PastebinSearch v{tool.version}")
            return
        elif args.update:
            installer = ToolInstaller()
            installer.update_tool()
            return
        elif args.donate:
            tool.show_donation_info()
            return
        elif args.diagnose:
            await tool.diagnose_connectivity()
            return
        elif args.install:
            installer = ToolInstaller()
            await installer.install()
            return
        elif args.test_deps:
            installer = ToolInstaller()
            await installer.test_optional_dependencies()
            return
        elif args.uninstall:
            installer = ToolInstaller()
            await installer.uninstall()
            return
        elif args.config:
            tool.show_banner()
            await tool.handle_config_menu()
            return
        elif args.search:
            await tool.quick_search(args.search)
            return
        elif args.manual:
            await tool.manual_search(args.manual)
            return
        else:
            # Interactive mode
            await tool.interactive_mode()
            
    except KeyboardInterrupt:
        tool.console.print("\n[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        tool.console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run the tool
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")


