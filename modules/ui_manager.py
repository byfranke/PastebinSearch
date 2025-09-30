
"""
UI Manager for PastebinSearch Tool
Handles all user interface elements and display functions
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich import box
from rich.tree import Tree
from rich.syntax import Syntax

class UIManager:
    """Manages user interface and display functions"""
    
    def __init__(self, console: Console):
        self.console = console
        self.theme_colors = {
            'primary': 'cyan',
            'secondary': 'yellow',
            'success': 'green',
            'warning': 'orange3',
            'error': 'red',
            'info': 'blue',
            'accent': 'magenta'
        }
    
    def show_banner(self, version: str):
        """Display the tool banner"""
        banner_art = f"""
[bold cyan]
██████╗  █████╗ ███████╗████████╗███████╗██████╗ ██╗███╗   ██╗    ███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║████╗  ██║    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
██████╔╝███████║███████╗   ██║   █████╗  ██████╔╝██║██╔██╗ ██║    ███████╗█████╗  ███████║██████╔╝██║     ███████║
██╔═══╝ ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║██║╚██╗██║    ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
██║     ██║  ██║███████║   ██║   ███████╗██████╔╝██║██║ ╚████║    ███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝    ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
[/bold cyan]

[bold white]                               🔍 Advanced Security Research Tool v{version} 🔍[/bold white]
[dim]                                     byFranke - https://byfranke.com[/dim]
        """
        
        info_panel = Panel(
            banner_art,
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        self.console.print(info_panel)
        
        # Show system info
        import platform
        import sys
        
        system_info = f"""
[green]🖥️  System:[/green] {platform.system()} {platform.release()}
[green]🐍 Python:[/green] {sys.version.split()[0]}
[green]⚡ Status:[/green] Ready for Security Research
[yellow]⚠️  Legal:[/yellow] Use responsibly and ethically only
        """
        
        self.console.print(Panel(
            system_info,
            title="System Information",
            border_style="green",
            padding=(0, 1)
        ))
        
        self.console.print()
    
    def show_main_menu(self) -> str:
        """Display main menu and get user choice"""
        menu_items = [
            ("1", "🔍 Search Options", "Perform searches with various filters"),
            ("2", "🌐 Browser Automation", "Manage browser automation features"),
            ("3", "⚙️  Configuration", "Manage tool settings and preferences"),
            ("4", "📊 Results Management", "View and manage search results"),
            ("5", "📋 Logs & History", "View logs and search history"),
            ("6", "ℹ️  About & Help", "Tool information and help"),
            ("0", "❌ Exit", "Close the application")
        ]
        
        menu_text = "\n".join([
            f"[{self.theme_colors['primary']}]{num}.[/{self.theme_colors['primary']}] "
            f"[bold]{title}[/bold] - {desc}"
            for num, title, desc in menu_items
        ])
        
        panel = Panel(
            menu_text,
            title="🏠 Main Menu",
            border_style=self.theme_colors['primary'],
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        return Prompt.ask(
            f"[{self.theme_colors['secondary']}]Select an option",
            choices=[item[0] for item in menu_items],
            default="1"
        )
    
    def show_search_menu(self) -> str:
        """Display search submenu"""
        menu_items = [
            ("1", "🔍 Quick Search", "Simple term search"),
            ("2", "🔧 Advanced Search", "Search with filters and options"),
            ("3", "📂 Batch Search", "Search multiple terms from file"),
            ("4", "📈 Search History", "View previous searches"),
            ("0", "🔙 Back to Main", "Return to main menu")
        ]
        
        menu_text = "\n".join([
            f"[{self.theme_colors['primary']}]{num}.[/{self.theme_colors['primary']}] "
            f"[bold]{title}[/bold] - {desc}"
            for num, title, desc in menu_items
        ])
        
        self.console.print(Panel(
            menu_text,
            title="🔍 Search Options",
            border_style=self.theme_colors['secondary']
        ))
        
        return Prompt.ask(
            f"[{self.theme_colors['secondary']}]Select search option",
            choices=[item[0] for item in menu_items],
            default="1"
        )
    
    def show_browser_menu(self) -> str:
        """Display browser automation submenu"""
        menu_items = [
            ("1", "🚀 Start Browser", "Launch automated browser"),
            ("2", "🎯 Auto Navigate", "Navigate to specific URLs"),
            ("3", "👁️  Monitor Changes", "Watch for page changes"),
            ("4", "🛑 Stop Browser", "Close browser session"),
            ("0", "🔙 Back to Main", "Return to main menu")
        ]
        
        menu_text = "\n".join([
            f"[{self.theme_colors['primary']}]{num}.[/{self.theme_colors['primary']}] "
            f"[bold]{title}[/bold] - {desc}"
            for num, title, desc in menu_items
        ])
        
        self.console.print(Panel(
            menu_text,
            title="🌐 Browser Automation",
            border_style=self.theme_colors['info']
        ))
        
        return Prompt.ask(
            f"[{self.theme_colors['secondary']}]Select browser option",
            choices=[item[0] for item in menu_items],
            default="1"
        )
    
    def show_config_menu(self) -> str:
        """Display configuration submenu"""
        menu_items = [
            ("1", "✏️  Edit Settings", "Interactive configuration editor"),
            ("2", "📤 Export Config", "Export configuration to file"),
            ("3", "📥 Import Config", "Import configuration from file"),
            ("4", "🔄 Reset to Defaults", "Reset all settings to default"),
            ("0", "🔙 Back to Main", "Return to main menu")
        ]
        
        menu_text = "\n".join([
            f"[{self.theme_colors['primary']}]{num}.[/{self.theme_colors['primary']}] "
            f"[bold]{title}[/bold] - {desc}"
            for num, title, desc in menu_items
        ])
        
        self.console.print(Panel(
            menu_text,
            title="⚙️ Configuration",
            border_style=self.theme_colors['warning']
        ))
        
        return Prompt.ask(
            f"[{self.theme_colors['secondary']}]Select config option",
            choices=[item[0] for item in menu_items],
            default="1"
        )
    
    def show_results_menu(self) -> str:
        """Display results management submenu"""
        menu_items = [
            ("1", "📊 Recent Results", "View recent search results"),
            ("2", "💾 Export Results", "Export results to various formats"),
            ("3", "🗑️  Clear Results", "Clear stored results"),
            ("0", "🔙 Back to Main", "Return to main menu")
        ]
        
        menu_text = "\n".join([
            f"[{self.theme_colors['primary']}]{num}.[/{self.theme_colors['primary']}] "
            f"[bold]{title}[/bold] - {desc}"
            for num, title, desc in menu_items
        ])
        
        self.console.print(Panel(
            menu_text,
            title="📊 Results Management",
            border_style=self.theme_colors['success']
        ))
        
        return Prompt.ask(
            f"[{self.theme_colors['secondary']}]Select results option",
            choices=[item[0] for item in menu_items],
            default="1"
        )
    
    def show_logs_menu(self) -> str:
        """Display logs submenu"""
        menu_items = [
            ("1", "📋 Recent Logs", "View recent activity logs"),
            ("2", "❌ Error Logs", "View error logs only"),
            ("3", "🧹 Clear Logs", "Clear all log files"),
            ("4", "📤 Export Logs", "Export logs to file"),
            ("0", "🔙 Back to Main", "Return to main menu")
        ]
        
        menu_text = "\n".join([
            f"[{self.theme_colors['primary']}]{num}.[/{self.theme_colors['primary']}] "
            f"[bold]{title}[/bold] - {desc}"
            for num, title, desc in menu_items
        ])
        
        self.console.print(Panel(
            menu_text,
            title="📋 Logs & History",
            border_style=self.theme_colors['accent']
        ))
        
        return Prompt.ask(
            f"[{self.theme_colors['secondary']}]Select logs option",
            choices=[item[0] for item in menu_items],
            default="1"
        )
    
    def display_results(self, results: List[Dict[str, Any]], search_term: str):
        """Display search results in a formatted table"""
        if not results:
            self.console.print(f"[{self.theme_colors['warning']}]⚠️  No results found for: {search_term}[/{self.theme_colors['warning']}]")
            return
        
        # Create results table
        table = Table(
            title=f"🔍 Search Results for: '{search_term}' ({len(results)} found)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Title", style="yellow", min_width=30)
        table.add_column("Date", style="green", width=12)
        table.add_column("Size", style="blue", width=8, justify="right")
        table.add_column("Syntax", style="magenta", width=10)
        table.add_column("URL", style="cyan", overflow="ellipsis", max_width=40)
        
        # Add rows
        for i, result in enumerate(results[:50], 1):  # Limit to 50 results for display
            title = result.get('title', 'Untitled')[:40]
            date = result.get('date', 'Unknown')
            size = self.format_size(result.get('size', 0))
            syntax = result.get('syntax', 'text')
            url = result.get('url', '')
            
            # Color code based on certain criteria
            if any(keyword in title.lower() for keyword in ['password', 'key', 'token', 'secret']):
                title_style = "bold red"
            elif any(keyword in title.lower() for keyword in ['database', 'db', 'sql']):
                title_style = "bold orange3"
            elif any(keyword in title.lower() for keyword in ['config', 'env', '.conf']):
                title_style = "bold yellow"
            else:
                title_style = "white"
            
            table.add_row(
                str(i),
                Text(title, style=title_style),
                date,
                size,
                syntax,
                url
            )
        
        self.console.print(table)
        
        # Show summary
        if len(results) > 50:
            self.console.print(f"\n[dim]Showing first 50 results. Total found: {len(results)}[/dim]")
        
        # Show security alerts if found
        sensitive_count = sum(1 for r in results 
                            if any(keyword in r.get('title', '').lower() 
                                 for keyword in ['password', 'key', 'token', 'secret', 'credential']))
        
        if sensitive_count > 0:
            alert_text = f"[bold red]🚨 SECURITY ALERT:[/bold red] Found {sensitive_count} potentially sensitive results!"
            self.console.print(Panel(
                alert_text,
                border_style="red",
                padding=(0, 1)
            ))
    
    def display_search_progress(self, current: int, total: int, status: str):
        """Display search progress"""
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(status, total=total)
            progress.update(task, completed=current)
    
    def show_error_message(self, title: str, message: str, details: Optional[str] = None):
        """Display error message in a formatted panel"""
        error_content = f"[bold red]❌ {title}[/bold red]\n\n{message}"
        
        if details:
            error_content += f"\n\n[dim]Details: {details}[/dim]"
        
        self.console.print(Panel(
            error_content,
            border_style="red",
            padding=(1, 2)
        ))
    
    def show_success_message(self, title: str, message: str):
        """Display success message in a formatted panel"""
        success_content = f"[bold green]✅ {title}[/bold green]\n\n{message}"
        
        self.console.print(Panel(
            success_content,
            border_style="green",
            padding=(1, 2)
        ))
    
    def show_warning_message(self, title: str, message: str):
        """Display warning message in a formatted panel"""
        warning_content = f"[bold yellow]⚠️  {title}[/bold yellow]\n\n{message}"
        
        self.console.print(Panel(
            warning_content,
            border_style="yellow",
            padding=(1, 2)
        ))
    
    def show_info_message(self, title: str, message: str):
        """Display info message in a formatted panel"""
        info_content = f"[bold blue]ℹ️  {title}[/bold blue]\n\n{message}"
        
        self.console.print(Panel(
            info_content,
            border_style="blue",
            padding=(1, 2)
        ))
    
    def display_search_stats(self, stats: Dict[str, Any]):
        """Display search statistics"""
        stats_table = Table(title="📈 Search Statistics", box=box.SIMPLE)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="yellow", justify="right")
        
        for metric, value in stats.items():
            stats_table.add_row(metric.replace('_', ' ').title(), str(value))
        
        self.console.print(stats_table)
    
    def show_configuration_tree(self, config: Dict[str, Any]):
        """Display configuration in a tree structure"""
        tree = Tree("🔧 Configuration", style="cyan")
        
        for section, values in config.items():
            section_branch = tree.add(f"[yellow]{section.title()}[/yellow]")
            
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, dict):
                        sub_branch = section_branch.add(f"[blue]{key}[/blue]")
                        for sub_key, sub_value in value.items():
                            sub_branch.add(f"{sub_key}: [green]{sub_value}[/green]")
                    else:
                        section_branch.add(f"{key}: [green]{value}[/green]")
            else:
                tree.add(f"{section}: [green]{values}[/green]")
        
        self.console.print(tree)
    
    def format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        if size == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def show_loading_spinner(self, message: str):
        """Show a loading spinner with message"""
        return self.console.status(f"[cyan]{message}[/cyan]")
    
    def clear_screen(self):
        """Clear the console screen"""
        self.console.clear()
    
    def print_separator(self, char: str = "─", style: str = "dim"):
        """Print a separator line"""
        width = self.console.size.width
        self.console.print(char * width, style=style)
    
    def show_keyboard_shortcuts(self):
        """Display keyboard shortcuts help"""
        shortcuts_text = """
[bold cyan]⌨️  Keyboard Shortcuts[/bold cyan]

[yellow]Navigation:[/yellow]
• Ctrl+C     - Cancel current operation / Exit menu
• Enter      - Confirm selection
• Tab        - Auto-complete (where available)

[yellow]Search:[/yellow]
• Ctrl+S     - Quick search
• Ctrl+A     - Advanced search
• Ctrl+H     - Search history

[yellow]General:[/yellow]
• Ctrl+Q     - Quit application
• F1         - Show help
• F5         - Refresh current view
        """
        
        self.console.print(Panel(
            shortcuts_text,
            title="Keyboard Shortcuts",
            border_style="blue"
        ))
    
    def show_ascii_art_logo(self):
        """Show ASCII art logo"""
        logo = """
[cyan]
██████╗  █████╗ ███████╗████████╗███████╗██████╗ ██╗███╗   ██╗
██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║████╗  ██║
██████╔╝███████║███████╗   ██║   █████╗  ██████╔╝██║██╔██╗ ██║
██╔═══╝ ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║██║╚██╗██║
██║     ██║  ██║███████║   ██║   ███████╗██████╔╝██║██║ ╚████║
╚═╝     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝

███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║
███████╗█████╗  ███████║██████╔╝██║     ███████║
╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
[/cyan]
        """
        self.console.print(logo)

