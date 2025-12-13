"""
UI components and utilities using Rich library
"""

import platform
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import List, Dict, Optional


console = Console()


class UI:
    """UI utilities for terminal interface"""
    
    @staticmethod
    def clear():
        """Clear the console screen"""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
    
    @staticmethod
    def print_header(title: str, subtitle: str = ""):
        """Print a styled header"""
        UI.clear()
        header = Text(title, style="bold cyan")
        if subtitle:
            header.append(f"\n{subtitle}", style="dim")
        
        console.print(Panel(header, border_style="cyan"))
        console.print()
    
    @staticmethod
    def print_success(message: str):
        """Print success message"""
        console.print(f"[bold green]✓[/bold green] {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print error message"""
        console.print(f"[bold red]✗[/bold red] {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Print warning message"""
        console.print(f"[bold yellow]⚠[/bold yellow] {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print info message"""
        console.print(f"[bold blue]ℹ[/bold blue] {message}")
    
    @staticmethod
    def prompt(message: str, default: str = "") -> str:
        """Get user input with prompt"""
        return Prompt.ask(f"[bold cyan]?[/bold cyan] {message}", default=default)
    
    @staticmethod
    def confirm(message: str, default: bool = False) -> bool:
        """Get yes/no confirmation from user"""
        return Confirm.ask(f"[bold cyan]?[/bold cyan] {message}", default=default)
    
    @staticmethod
    def create_menu(title: str, options: List[str]) -> Table:
        """Create a menu table"""
        table = Table(title=title, show_header=False, border_style="cyan")
        table.add_column("Option", style="cyan", width=5)
        table.add_column("Description", style="white")
        
        for i, option in enumerate(options, 1):
            table.add_row(f"[{i}]", option)
        
        return table
    
    @staticmethod
    def display_table(data: List[Dict], columns: List[tuple], title: str = ""):
        """
        Display data in a table
        
        Args:
            data: List of dicts containing row data
            columns: List of (column_name, dict_key, style) tuples
            title: Optional table title
        """
        table = Table(title=title, border_style="cyan")
        
        for col_name, _, style in columns:
            table.add_column(col_name, style=style)
        
        for row in data:
            table.add_row(*[str(row.get(key, "N/A")) for _, key, _ in columns])
        
        console.print(table)
    
    @staticmethod
    def display_game_search_results(games: List[Dict]):
        """Display game search results in a formatted table"""
        if not games:
            UI.print_warning("No games found")
            return
        
        table = Table(title="Search Results", border_style="cyan")
        table.add_column("#", style="cyan", width=4)
        table.add_column("App ID", style="yellow")
        table.add_column("Game Name", style="white")
        
        for i, game in enumerate(games, 1):
            table.add_row(
                str(i),
                str(game['appid']),
                game['name']
            )
        
        console.print(table)
    
    @staticmethod
    def create_progress_spinner(message: str = "Loading..."):
        """Create a progress spinner context manager"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        )
    
    @staticmethod
    def print_online_fix_guide():
        """Display comprehensive online fix guide"""
        UI.clear()
        
        guide_text = """[bold cyan]🎮 Online Multiplayer Fix Guide[/bold cyan]

[bold yellow]What is this?[/bold yellow]
This feature enables online multiplayer for certain games by routing their network
traffic through Spacewar (AppID 480). This is useful for games that don't have
proper multiplayer support in their current state.

[bold yellow]How it works:[/bold yellow]
• Adds an entry to the FakeAppIds section of your SLSsteam config
• Routes the game's network traffic through Steam's Spacewar test app
• Both players must use the same routing for multiplayer to work

[bold yellow]Known Compatible Games:[/bold yellow]
The following games are known to work well with this method:

[bold green]Fighting Games:[/bold green]
  • Street Fighter V (359550)
  • Mortal Kombat 11 (976310)
  • Guilty Gear Strive (1384160)
  • Dragon Ball FighterZ (678950)

[bold green]Co-op Games:[/bold green]
  • Portal 2 (620)
  • Left 4 Dead 2 (550)
  • Don't Starve Together (322330)
  • Terraria (105600)

[bold green]Strategy Games:[/bold green]
  • Civilization VI (289070)
  • Age of Empires II: Definitive Edition (813780)

[bold yellow]Important Notes:[/bold yellow]
• Not guaranteed to work for all games
• Games with anti-cheat may not work
• Games requiring dedicated servers may not work
• Both players MUST use the same method
• Some games may have degraded performance

[bold yellow]Troubleshooting:[/bold yellow]
• If it doesn't work, try restarting Steam/SLSsteam
• Check firewall settings
• Ensure you and your friend are both using Spacewar routing
• Some games require additional configuration

[bold red]Disclaimer:[/bold red]
This is an experimental feature. Results may vary by game.
Always check game-specific communities for additional guidance.
"""
        
        console.print(Panel(guide_text, border_style="cyan", padding=(1, 2)))
        console.print()
        input("Press Enter to continue...")
    
    @staticmethod
    def print_version_info(version: str):
        """Display version information"""
        version_text = f"""[bold cyan]SLS-AH (SLSsteam Achievement Helper)[/bold cyan]
Version: [bold yellow]{version}[/bold yellow]

A power-user's toolkit for Steam on Linux/Steam Deck
Achievement schema generation and SLSsteam integration

Repository: [link]https://github.com/niwia/SLSah[/link]
License: GNU Lesser General Public License v3.0
"""
        console.print(Panel(version_text, border_style="cyan", padding=(1, 2)))
