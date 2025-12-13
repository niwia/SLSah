#!/usr/bin/env python3
"""
SLS-AH (SLSsteam Achievement Helper) - Main Entry Point
Version 2.0 - Modular Architecture
"""

import sys
import os
import argparse

# Add lib directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from __version__ import __version__
from lib.credentials import CredentialManager
from lib.steam_api import SteamAPI
from lib.config_manager import ConfigManager
from lib.ui import UI, console

# Import legacy modules for gradual migration
import generate_schema_from_api as legacy_generator
import sls_manager as legacy_manager


def setup_credentials():
    """Setup or load encrypted credentials"""
    cred_manager = CredentialManager()
    
    # Try to migrate from old .env file
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path) and not cred_manager.credentials_exist():
        UI.print_info("Found old .env credentials. Migrating to encrypted storage...")
        if cred_manager.migrate_from_dotenv(dotenv_path):
            UI.print_success("Credentials migrated successfully!")
        else:
            UI.print_warning("Could not migrate credentials. Please re-enter them.")
    
    # Load existing credentials
    creds = cred_manager.load_credentials()
    
    if creds:
        api_key, steam_id = creds
        UI.print_success("Credentials loaded from encrypted storage")
        return api_key, steam_id, cred_manager
    
    # Prompt for new credentials
    UI.print_header("Credential Setup", "First time setup - your credentials will be encrypted")
    
    console.print("\n[bold yellow]Steam API Key[/bold yellow]")
    console.print("Get one from: [cyan]https://steamcommunity.com/dev/apikey[/cyan]")
    api_key = UI.prompt("Enter your Steam API Key").strip()
    
    console.print("\n[bold yellow]Steam User ID[/bold yellow]")
    console.print("Find yours at: [cyan]https://steamid.io/[/cyan]")
    console.print("Example format: [dim][U:1:xxxxxxxxx][/dim]")
    steam_id_input = UI.prompt("Enter your Steam User ID").strip()
    
    # Extract numeric ID from various formats
    import re
    match = re.search(r'(\d+)]?$', steam_id_input)
    if match:
        steam_id = match.group(1)
    else:
        steam_id = steam_id_input
    
    # Verify credentials
    UI.print_info("Verifying API key...")
    steam_api = SteamAPI(api_key)
    
    if steam_api.verify_api_key(steam_id):
        UI.print_success("API key verified!")
        cred_manager.save_credentials(api_key, steam_id)
        UI.print_success("Credentials saved in encrypted storage")
    else:
        UI.print_error("Failed to verify API key. Please check your credentials.")
        sys.exit(1)
    
    steam_api.close()
    return api_key, steam_id, cred_manager


def handle_game_search(steam_api: SteamAPI):
    """Handle interactive game search"""
    UI.clear()
    UI.print_header("🔍 Search Games", "Search Steam store by game name")
    
    query = UI.prompt("Enter game name to search")
    
    if not query:
        return None
    
    with UI.create_progress_spinner("Searching Steam store...") as progress:
        task = progress.add_task("", total=None)
        games = steam_api.search_games(query, max_results=10)
    
    if not games:
        UI.print_warning("No games found")
        input("\nPress Enter to continue...")
        return None
    
    UI.display_game_search_results(games)
    
    choice = UI.prompt("\nSelect game number (or 'b' to go back)")
    
    if choice.lower() == 'b':
        return None
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(games):
            selected_game = games[index]
            return selected_game['appid']
        else:
            UI.print_error("Invalid selection")
            return None
    except ValueError:
        UI.print_error("Invalid input")
        return None


def main():
    """Main application entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='SLS-AH - SLSsteam Achievement Helper',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-v', '--version', action='version', 
                       version=f'SLS-AH v{__version__}')
    parser.add_argument('--clear-credentials', action='store_true',
                       help='Clear stored credentials')
    
    args = parser.parse_args()
    
    # Note: --version is handled automatically by argparse action='version'
    
    # Handle credential clearing
    if args.clear_credentials:
        cred_manager = CredentialManager()
        cred_manager.clear_credentials()
        UI.print_success("Credentials cleared")
        return
    
    # Check internet connection
    if not legacy_generator.check_internet_connection():
        UI.print_error("No internet connection detected")
        sys.exit(1)
    
    # Setup credentials
    api_key, steam_id, cred_manager = setup_credentials()
    
    # Main menu loop
    language = 'english'
    
    while True:
        UI.print_header(
            f"SLS-AH v{__version__}",
            f"Language: {language} | Steam ID: {steam_id}"
        )
        
        options = [
            "Generate from SLSsteam config",
            "Scan Steam library for games",
            "Manual App ID input",
            "🔍 Search for game by name",
            "",  # Separator
            "Manage SLSsteam App List",
            "Purge generated schemas",
            "📖 View Online Fix Guide",
            "",  # Separator
            "Change Language",
            "Clear Credentials",
            "Update Tool",
            "Uninstall Tool"
        ]
        
        menu = UI.create_menu("Main Menu", options)
        console.print(menu)
        console.print()
        console.print(f"[dim]Version {__version__}[/dim]")
        console.print()
        
        choice = UI.prompt("Select an option (q to quit)")
        
        if choice.lower() == 'q':
            break
        
        # Handle menu choices
        try:
            choice_num = int(choice)
            
            if choice_num == 1:
                legacy_generator.handle_slssteam_list(api_key, steam_id, language)
            elif choice_num == 2:
                legacy_generator.handle_steam_library(api_key, steam_id, language)
            elif choice_num == 3:
                legacy_generator.handle_manual_input(api_key, steam_id, language)
            elif choice_num == 4:
                # New game search feature
                steam_api = SteamAPI(api_key)
                app_id = handle_game_search(steam_api)
                steam_api.close()
                
                if app_id:
                    summary = {'total': 0, 'overwritten': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
                    legacy_generator.get_game_schema(api_key, steam_id, str(app_id), summary, language, 'ask')
                    legacy_generator.print_summary(summary)
                    input("\nPress Enter to continue...")
            elif choice_num == 6:
                legacy_manager.main()
            elif choice_num == 7:
                legacy_generator.handle_purge_menu(steam_id)
            elif choice_num == 8:
                # Show online fix guide
                UI.print_online_fix_guide()
            elif choice_num == 10:
                new_lang = legacy_generator.change_language()
                if new_lang:
                    language = new_lang
            elif choice_num == 11:
                if UI.confirm("Are you sure you want to clear credentials?"):
                    cred_manager.clear_credentials()
                    UI.print_success("Credentials cleared. Restart to set up again.")
                    break
            elif choice_num == 12:
                legacy_generator.handle_update()
                break
            elif choice_num == 13:
                if UI.confirm("Are you sure you want to uninstall?"):
                    legacy_generator.handle_uninstall()
                    break
            else:
                UI.print_error("Invalid option")
                input("\nPress Enter to continue...")
        
        except ValueError:
            UI.print_error("Please enter a number")
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted by user[/yellow]")
            break
        except Exception as e:
            UI.print_error(f"An error occurred: {e}")
            input("\nPress Enter to continue...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Exiting...[/yellow]")
        sys.exit(0)
