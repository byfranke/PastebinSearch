"""
Logger for PastebinSearch Tool
Handles logging, search history, and activity tracking
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

class SearchLogger:
    """Manages logging and search history for PastebinSearch"""
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path(__file__).parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Log files
        self.search_log_file = self.log_dir / "search_history.json"
        self.error_log_file = self.log_dir / "errors.log"
        self.activity_log_file = self.log_dir / "activity.log"
        
        # Setup logging
        self.setup_logging()
        
        # In-memory caches
        self.search_history: List[Dict[str, Any]] = []
        self.load_search_history()
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)8s | %(name)s | %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        
        # Setup main logger
        self.logger = logging.getLogger('PastebinSearch')
        self.logger.setLevel(logging.INFO)
        
        # File handler for general activity
        activity_handler = logging.FileHandler(self.activity_log_file)
        activity_handler.setLevel(logging.INFO)
        activity_handler.setFormatter(detailed_formatter)
        
        # File handler for errors
        error_handler = logging.FileHandler(self.error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers
        self.logger.addHandler(activity_handler)
        self.logger.addHandler(error_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def log_search(self, search_term: str, results_count: int, 
                  filters: Optional[Dict[str, Any]] = None, 
                  duration: Optional[float] = None):
        """Log a search operation"""
        timestamp = datetime.now().isoformat()
        
        search_entry = {
            'timestamp': timestamp,
            'search_term': search_term,
            'results_count': results_count,
            'filters': filters or {},
            'duration': duration,
            'type': 'search'
        }
        
        # Add to history
        self.search_history.append(search_entry)
        
        # Save to file
        self.save_search_history()
        
        # Log to activity log
        filter_info = f" with filters: {filters}" if filters else ""
        duration_info = f" in {duration:.2f}s" if duration else ""
        
        self.logger.info(
            f"Search: '{search_term}' returned {results_count} results{filter_info}{duration_info}"
        )
        
        print(f"📝 Search logged: {search_term} ({results_count} results)")
    
    def log_error(self, error_message: str, error_type: str = "general", 
                 context: Optional[Dict[str, Any]] = None):
        """Log an error"""
        timestamp = datetime.now().isoformat()
        
        error_entry = {
            'timestamp': timestamp,
            'error_type': error_type,
            'message': error_message,
            'context': context or {},
            'type': 'error'
        }
        
        # Log to error file
        context_info = f" Context: {context}" if context else ""
        self.logger.error(f"[{error_type}] {error_message}{context_info}")
        
        print(f"❌ Error logged: {error_type} - {error_message}")
    
    def log_activity(self, activity: str, details: Optional[Dict[str, Any]] = None):
        """Log general activity"""
        timestamp = datetime.now().isoformat()
        
        activity_entry = {
            'timestamp': timestamp,
            'activity': activity,
            'details': details or {},
            'type': 'activity'
        }
        
        # Log to activity file
        details_info = f" Details: {details}" if details else ""
        self.logger.info(f"Activity: {activity}{details_info}")
    
    def load_search_history(self):
        """Load search history from file"""
        try:
            if self.search_log_file.exists():
                with open(self.search_log_file, 'r', encoding='utf-8') as f:
                    self.search_history = json.load(f)
        except Exception as e:
            self.log_error(f"Failed to load search history: {e}")
            self.search_history = []
    
    def save_search_history(self):
        """Save search history to file"""
        try:
            # Keep only last 1000 entries
            if len(self.search_history) > 1000:
                self.search_history = self.search_history[-1000:]
            
            with open(self.search_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_error(f"Failed to save search history: {e}")
    
    def get_search_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent search history"""
        return self.search_history[-limit:] if self.search_history else []
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics"""
        if not self.search_history:
            return {
                'total_searches': 0,
                'unique_terms': 0,
                'average_results': 0,
                'most_searched_term': None,
                'search_frequency_by_day': {}
            }
        
        total_searches = len(self.search_history)
        unique_terms = len(set(entry['search_term'] for entry in self.search_history))
        
        # Calculate average results
        results_counts = [entry['results_count'] for entry in self.search_history if entry['results_count'] is not None]
        average_results = sum(results_counts) / len(results_counts) if results_counts else 0
        
        # Find most searched term
        term_counts = {}
        for entry in self.search_history:
            term = entry['search_term']
            term_counts[term] = term_counts.get(term, 0) + 1
        
        most_searched_term = max(term_counts, key=term_counts.get) if term_counts else None
        
        # Search frequency by day
        frequency_by_day = {}
        for entry in self.search_history:
            try:
                date = datetime.fromisoformat(entry['timestamp']).date().isoformat()
                frequency_by_day[date] = frequency_by_day.get(date, 0) + 1
            except:
                continue
        
        return {
            'total_searches': total_searches,
            'unique_terms': unique_terms,
            'average_results': round(average_results, 2),
            'most_searched_term': most_searched_term,
            'most_searched_count': term_counts.get(most_searched_term, 0) if most_searched_term else 0,
            'search_frequency_by_day': frequency_by_day
        }
    
    def show_recent_logs(self, console: Console, limit: int = 20):
        """Display recent activity logs"""
        try:
            if not self.activity_log_file.exists():
                console.print("[yellow]⚠️  No activity logs found[/yellow]")
                return
            
            # Read last N lines from activity log
            with open(self.activity_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            if not recent_lines:
                console.print("[yellow]⚠️  No recent activity[/yellow]")
                return
            
            # Create table
            table = Table(
                title=f"📋 Recent Activity (Last {len(recent_lines)} entries)",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold cyan"
            )
            
            table.add_column("Time", style="green", width=20)
            table.add_column("Level", style="yellow", width=10)
            table.add_column("Message", style="white", min_width=50)
            
            for line in recent_lines:
                try:
                    parts = line.strip().split(' | ', 3)
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        level = parts[1].strip()
                        message = parts[3]
                        
                        # Color code based on level
                        if level == 'ERROR':
                            level_style = "bold red"
                        elif level == 'WARNING':
                            level_style = "bold yellow"
                        elif level == 'INFO':
                            level_style = "bold green"
                        else:
                            level_style = "white"
                        
                        table.add_row(
                            timestamp,
                            f"[{level_style}]{level}[/{level_style}]",
                            message[:80] + "..." if len(message) > 80 else message
                        )
                except:
                    continue
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]❌ Error reading logs: {e}[/red]")
    
    def show_error_logs(self, console: Console, limit: int = 20):
        """Display recent error logs"""
        try:
            if not self.error_log_file.exists():
                console.print("[yellow]⚠️  No error logs found[/yellow]")
                return
            
            # Read error log
            with open(self.error_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            recent_errors = lines[-limit:] if len(lines) > limit else lines
            
            if not recent_errors:
                console.print("[green]✅ No recent errors![/green]")
                return
            
            # Create table
            table = Table(
                title=f"❌ Recent Errors (Last {len(recent_errors)} entries)",
                box=box.ROUNDED,
                show_header=True,
                header_style="bold red"
            )
            
            table.add_column("Time", style="cyan", width=20)
            table.add_column("Error Message", style="red", min_width=60)
            
            for line in recent_errors:
                try:
                    parts = line.strip().split(' | ', 3)
                    if len(parts) >= 4:
                        timestamp = parts[0]
                        message = parts[3]
                        
                        table.add_row(
                            timestamp,
                            message[:100] + "..." if len(message) > 100 else message
                        )
                except:
                    continue
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]❌ Error reading error logs: {e}[/red]")
    
    def show_search_history_table(self, console: Console, limit: int = 20):
        """Display search history in table format"""
        history = self.get_search_history(limit)
        
        if not history:
            console.print("[yellow]⚠️  No search history found[/yellow]")
            return
        
        # Create table
        table = Table(
            title=f"🔍 Search History (Last {len(history)} searches)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Date/Time", style="green", width=20)
        table.add_column("Search Term", style="yellow", min_width=30)
        table.add_column("Results", style="blue", width=10, justify="right")
        table.add_column("Duration", style="magenta", width=10, justify="right")
        
        for i, entry in enumerate(reversed(history), 1):
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")
                
                search_term = entry['search_term']
                if len(search_term) > 40:
                    search_term = search_term[:37] + "..."
                
                results_count = str(entry['results_count']) if entry['results_count'] is not None else "N/A"
                
                duration = f"{entry['duration']:.2f}s" if entry.get('duration') else "N/A"
                
                table.add_row(
                    str(i),
                    formatted_time,
                    search_term,
                    results_count,
                    duration
                )
            except:
                continue
        
        console.print(table)
    
    def show_statistics(self, console: Console):
        """Display search statistics"""
        stats = self.get_search_stats()
        
        # Create statistics panel
        stats_text = f"""
[cyan]📊 Search Statistics[/cyan]

[green]General Stats:[/green]
• Total Searches: {stats['total_searches']}
• Unique Terms: {stats['unique_terms']}
• Average Results: {stats['average_results']}

[green]Most Popular:[/green]
• Most Searched: "{stats['most_searched_term']}" ({stats['most_searched_count']} times)

[green]Activity:[/green]
• Active Days: {len(stats['search_frequency_by_day'])}
        """
        
        console.print(Panel(
            stats_text,
            title="Statistics",
            border_style="blue",
            padding=(1, 2)
        ))
        
        # Show recent activity chart
        if stats['search_frequency_by_day']:
            recent_days = dict(list(stats['search_frequency_by_day'].items())[-7:])
            
            activity_table = Table(title="📈 Recent Activity (Last 7 Days)", box=box.SIMPLE)
            activity_table.add_column("Date", style="cyan")
            activity_table.add_column("Searches", style="yellow", justify="right")
            activity_table.add_column("Activity", style="green")
            
            for date, count in recent_days.items():
                # Create simple bar chart
                bar = "█" * min(count, 20) + "░" * (20 - min(count, 20))
                activity_table.add_row(date, str(count), bar)
            
            console.print(activity_table)
    
    def clear_logs(self):
        """Clear all log files"""
        try:
            # Clear search history
            self.search_history = []
            if self.search_log_file.exists():
                self.search_log_file.unlink()
            
            # Clear activity log
            if self.activity_log_file.exists():
                self.activity_log_file.unlink()
            
            # Clear error log
            if self.error_log_file.exists():
                self.error_log_file.unlink()
            
            # Recreate logging setup
            self.setup_logging()
            
            print("✅ All logs cleared successfully")
            self.log_activity("Logs cleared by user")
            
        except Exception as e:
            print(f"❌ Error clearing logs: {e}")
    
    def export_logs(self, export_path: Optional[Path] = None):
        """Export logs to a single file"""
        try:
            if not export_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = Path(f"logs_export_{timestamp}.json")
            
            export_data = {
                'export_date': datetime.now().isoformat(),
                'search_history': self.search_history,
                'statistics': self.get_search_stats()
            }
            
            # Add recent activity logs if available
            if self.activity_log_file.exists():
                with open(self.activity_log_file, 'r', encoding='utf-8') as f:
                    export_data['activity_logs'] = f.readlines()[-100:]  # Last 100 entries
            
            # Add recent error logs if available
            if self.error_log_file.exists():
                with open(self.error_log_file, 'r', encoding='utf-8') as f:
                    export_data['error_logs'] = f.readlines()[-50:]  # Last 50 entries
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Logs exported to: {export_path}")
            self.log_activity(f"Logs exported to {export_path}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            self.log_error(f"Log export failed: {e}")
    
    def search_logs(self, search_term: str, log_type: str = "all") -> List[Dict[str, Any]]:
        """Search through logs for specific terms"""
        results = []
        
        try:
            if log_type in ["all", "search"] and self.search_history:
                for entry in self.search_history:
                    if search_term.lower() in entry['search_term'].lower():
                        results.append({
                            'type': 'search',
                            'entry': entry
                        })
            
            if log_type in ["all", "activity"] and self.activity_log_file.exists():
                with open(self.activity_log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if search_term.lower() in line.lower():
                            results.append({
                                'type': 'activity',
                                'line_number': line_num,
                                'content': line.strip()
                            })
            
            if log_type in ["all", "error"] and self.error_log_file.exists():
                with open(self.error_log_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if search_term.lower() in line.lower():
                            results.append({
                                'type': 'error',
                                'line_number': line_num,
                                'content': line.strip()
                            })
        
        except Exception as e:
            self.log_error(f"Log search failed: {e}")
        
        return results
