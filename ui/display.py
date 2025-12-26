from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich import box
from typing import List, Dict, Any
from core.plugin_base import PluginBase, PluginResult
from core.result_handler import ResultAggregator


console = Console()


def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║    ██████╗ ███████╗██╗███╗   ██╗████████╗    ████████╗ ██████║
║   ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝    ╚══██╔══╝██╔═══║
║   ██║   ██║███████╗██║██╔██╗ ██║   ██║          ██║   ██║   ║
║   ██║   ██║╚════██║██║██║╚██╗██║   ██║          ██║   ██║   ║
║   ╚██████╔╝███████║██║██║ ╚████║   ██║          ██║   ╚██████║
║    ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝          ╚═╝    ╚═════║
║                                                               ║
║              Open Source Intelligence Framework              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def print_success(message: str):
    console.print(f"✓ {message}", style="bold green")


def print_error(message: str):
    console.print(f"✗ {message}", style="bold red")


def print_warning(message: str):
    console.print(f"⚠ {message}", style="bold yellow")


def print_info(message: str):
    console.print(f"ℹ {message}", style="bold blue")


def display_plugins(plugins: List[PluginBase]):
    if not plugins:
        print_warning("No plugins available")
        return
    
    table = Table(title="Available OSINT Plugins", box=box.ROUNDED)
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Plugin Name", style="magenta bold")
    table.add_column("Description", style="white")
    table.add_column("Search Types", style="green")
    table.add_column("Status", style="yellow")
    
    for idx, plugin in enumerate(plugins, 1):
        search_types = ", ".join([st.value for st in plugin.supported_search_types])
        status = "✓ Enabled" if plugin.enabled else "✗ Disabled"
        status_style = "green" if plugin.enabled else "red"
        
        table.add_row(
            str(idx),
            plugin.name,
            plugin.description,
            search_types,
            Text(status, style=status_style)
        )
    
    console.print(table)


def display_results_summary(aggregator: ResultAggregator):
    console.print("\n")
    console.print(Panel(
        aggregator.get_summary(),
        title="Search Results Summary",
        border_style="cyan"
    ))


def display_results_detailed(aggregator: ResultAggregator):
    results = aggregator.results
    
    if not results:
        print_warning("No results to display")
        return
    
    for result in results:
        if result.success:
            _display_success_result(result)
        else:
            _display_failed_result(result)


def _display_success_result(result: PluginResult):
    panel_title = f"✓ {result.plugin_name} - Success"
    
    content = f"[bold]Query:[/bold] {result.query}\n"
    content += f"[bold]Search Type:[/bold] {result.search_type.value}\n"
    content += f"[bold]Timestamp:[/bold] {result.timestamp}\n\n"
    
    if result.data:
        content += "[bold cyan]Results:[/bold cyan]\n"
        tree = Tree("Data")
        _build_tree(tree, result.data)
        console.print(Panel(content, title=panel_title, border_style="green"))
        console.print(tree)
    else:
        content += "[yellow]No data returned[/yellow]"
        console.print(Panel(content, title=panel_title, border_style="green"))
    
    console.print("\n")


def _display_failed_result(result: PluginResult):
    panel_title = f"✗ {result.plugin_name} - Failed"
    
    content = f"[bold]Query:[/bold] {result.query}\n"
    content += f"[bold]Search Type:[/bold] {result.search_type.value}\n"
    content += f"[bold]Timestamp:[/bold] {result.timestamp}\n\n"
    content += f"[bold red]Error:[/bold red] {result.error}"
    
    console.print(Panel(content, title=panel_title, border_style="red"))
    console.print("\n")


def _build_tree(tree: Tree, data: Any, max_depth: int = 3, current_depth: int = 0):
    if current_depth >= max_depth:
        tree.add("[yellow]...[/yellow]")
        return
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                branch = tree.add(f"[cyan]{key}[/cyan]")
                _build_tree(branch, value, max_depth, current_depth + 1)
            else:
                tree.add(f"[cyan]{key}:[/cyan] {value}")
    elif isinstance(data, list):
        for idx, item in enumerate(data[:10]):
            if isinstance(item, (dict, list)):
                branch = tree.add(f"[yellow]Item {idx + 1}[/yellow]")
                _build_tree(branch, item, max_depth, current_depth + 1)
            else:
                tree.add(f"[yellow]{idx + 1}:[/yellow] {item}")
        if len(data) > 10:
            tree.add(f"[yellow]... and {len(data) - 10} more items[/yellow]")
    else:
        tree.add(str(data))


def display_export_results(export_paths: Dict[str, Any]):
    console.print("\n")
    table = Table(title="Export Results", box=box.ROUNDED)
    table.add_column("Format", style="cyan")
    table.add_column("File Path", style="green")
    
    for format_type, path in export_paths.items():
        table.add_row(format_type.upper(), str(path))
    
    console.print(table)
    print_success("All exports completed successfully!")


def prompt_continue() -> bool:
    try:
        response = console.input("\n[bold cyan]Press Enter to continue or 'q' to quit:[/bold cyan] ")
        return response.lower() != 'q'
    except (EOFError, KeyboardInterrupt):
        return False


def clear_screen():
    console.clear()
