"""Output formatters for CLI."""

from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

console = Console()


class OutputFormatter:
    """Formats and displays output in the CLI."""
    
    @staticmethod
    def print_header(title: str) -> None:
        """Print a formatted header.
        
        Args:
            title: Header title
        """
        console.print()
        console.print(f"[bold cyan]{title}[/bold cyan]")
        console.print("=" * len(title))
        console.print()
    
    @staticmethod
    def print_success(message: str) -> None:
        """Print a success message.
        
        Args:
            message: Success message
        """
        console.print(f"[green]✓[/green] {message}")
    
    @staticmethod
    def print_error(message: str) -> None:
        """Print an error message.
        
        Args:
            message: Error message
        """
        console.print(f"[red]✗[/red] {message}", style="red")
    
    @staticmethod
    def print_warning(message: str) -> None:
        """Print a warning message.
        
        Args:
            message: Warning message
        """
        console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")
    
    @staticmethod
    def print_info(message: str) -> None:
        """Print an info message.
        
        Args:
            message: Info message
        """
        console.print(f"[blue]ℹ[/blue] {message}")
    
    @staticmethod
    def print_markdown(content: str, title: Optional[str] = None) -> None:
        """Print markdown content.
        
        Args:
            content: Markdown content
            title: Optional panel title
        """
        md = Markdown(content)
        if title:
            panel = Panel(md, title=title, border_style="cyan")
            console.print(panel)
        else:
            console.print(md)
    
    @staticmethod
    def print_result(result: Dict[str, Any]) -> None:
        """Print research result.
        
        Args:
            result: Result dictionary
        """
        console.print()
        console.print(Panel(
            f"[bold]Query:[/bold] {result.get('query', 'N/A')}",
            title="Research Result",
            border_style="green"
        ))
        console.print()
        
        response = result.get('response', '')
        if response:
            OutputFormatter.print_markdown(response)
        
        if 'saved_path' in result:
            console.print()
            OutputFormatter.print_success(f"Results saved to: {result['saved_path']}")
        
        if 'report_path' in result:
            OutputFormatter.print_success(f"Report exported to: {result['report_path']}")
        
        console.print()
    
    @staticmethod
    def print_history(history: List[Dict[str, Any]]) -> None:
        """Print research history as a table.
        
        Args:
            history: List of history records
        """
        if not history:
            OutputFormatter.print_warning("No research history found.")
            return
        
        table = Table(title="Research History", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=6)
        table.add_column("Query", style="cyan", no_wrap=False)
        table.add_column("Timestamp", style="magenta")
        table.add_column("Filename", style="green")
        
        for i, record in enumerate(history, 1):
            table.add_row(
                str(i),
                record.get('query', 'N/A')[:60] + "..." if len(record.get('query', '')) > 60 else record.get('query', 'N/A'),
                record.get('timestamp', 'N/A'),
                record.get('filename', 'N/A')
            )
        
        console.print(table)
    
    @staticmethod
    def create_progress() -> Progress:
        """Create a progress indicator.
        
        Returns:
            Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        )
    
    @staticmethod
    def prompt(message: str) -> str:
        """Prompt user for input.
        
        Args:
            message: Prompt message
            
        Returns:
            User input string
        """
        return console.input(f"[cyan]{message}[/cyan] ")
