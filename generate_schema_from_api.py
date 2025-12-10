import requests
import sys
import os
import vdf
import json
import shutil
import yaml
from dotenv import load_dotenv, set_key
import re
import platform
from pathlib import Path
import socket
from rich.console import Console
from rich.table import Table

# --- FIX: Removed 'import sls_manager' to prevent circular import ---
from shared_utils import read_cache, write_cache, get_app_details, get_env_value

# --- Rich Console Initialization ---
console = Console()

# --- Constants ---
DOTENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.steam/steam/appcache/stats")
SLSSTEAM_CONFIG_PATH = os.path.expanduser("~/.config/SLSsteam/config.yaml")

def clear():
    """Clears the console screen."""
    console.clear()

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Check for internet connectivity."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        console.print("[bold red]No internet connection. Please check your network settings.[/bold red]")
        return False

def deep_merge(source, destination):
    """Recursively merges two dictionaries."""
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            destination[key] = value
    return destination

def get_achievement_names_from_schema(schema, app_id):
    """Extracts a set of achievement API names from a schema dictionary."""
    names = set()
    try:
        stats = schema[str(app_id)]['stats']
        for block in stats.values():
            if 'bits' in block:
                for ach in block['bits'].values():
                    names.add(ach['name'])
    except (KeyError, AttributeError):
        pass
    return names

def get_game_schema(api_key, steam_id, app_id, summary, language, batch_mode='ask'):
    """Fetches the game schema from the Steam Web API and processes it."""
    try:
        url = f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={app_id}&l={language}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data.get('game'):
            console.print(f"[bold red]Error processing App ID {app_id}:[/bold red] No game data in response. The App ID might be invalid or not released.")
            summary['errors'] += 1
            return False

        game_name = data['game']['gameName']
        console.print(f"--- Processing [bold cyan]{game_name}[/bold cyan] ({app_id}) ---")

        new_schema = {
            app_id: {
                "gamename": game_name,
                "version": data['game']['gameVersion'],
                "stats": {}
            }
        }
        if 'availableGameStats' in data['game'] and 'achievements' in data['game']['availableGameStats']:
            achievements = data['game']['availableGameStats']['achievements']
            for i, ach in enumerate(achievements):
                block_id = (i // 32) + 1
                bit_id = i % 32
                if str(block_id) not in new_schema[app_id]["stats"]:
                    new_schema[app_id]["stats"][str(block_id)] = {"type": "4", "id": str(block_id), "bits": {}}
                new_schema[app_id]["stats"][str(block_id)]["bits"][str(bit_id)] = {
                    "name": ach['name'], "bit": bit_id,
                    "display": {
                        "name": {language: ach['displayName'], "token": f"NEW_ACHIEVEMENT_{block_id}_{bit_id}_NAME"},
                        "desc": {language: ach.get('description', ''), "token": f"NEW_ACHIEVEMENT_{block_id}_{bit_id}_DESC"},
                        "hidden": str(ach['hidden']), "icon": ach['icon'].split('/')[-1], "icon_gray": ach['icongray'].split('/')[-1]
                    }
                }
        
        if not os.path.exists(DEFAULT_OUTPUT_DIR):
            os.makedirs(DEFAULT_OUTPUT_DIR)
            
        schema_filename = os.path.join(DEFAULT_OUTPUT_DIR, f"UserGameStatsSchema_{app_id}.bin")
        action = 'ask' if batch_mode == 'ask' else batch_mode

        if os.path.exists(schema_filename):
            if action == 'ask':
                try:
                    with open(schema_filename, 'rb') as f: existing_schema = vdf.binary_load(f)
                    existing_ach_names = get_achievement_names_from_schema(existing_schema, app_id)
                    new_ach_names = get_achievement_names_from_schema(new_schema, app_id)
                    new_achievements = new_ach_names - existing_ach_names
                    
                    if not new_achievements:
                        console.print("[green]Schema is already up-to-date. No new achievements found.[/green]")
                        action = 'skip'
                    else:
                        console.print(f"[yellow]Found {len(new_achievements)} new achievement(s).[/yellow]")
                        choice = console.input("Would you like to [1] Update (merge), [2] Overwrite, or [3] Skip? ")
                        if choice == '1': action = 'update'
                        elif choice == '2': action = 'overwrite'
                        else: action = 'skip'
                except Exception as e:
                    console.print(f"[bold red]Could not compare schema files: {e}[/bold red]")
                    choice = console.input(f"'{os.path.basename(schema_filename)}' already exists. [1] Overwrite, [2] Update, [3] Skip? ")
                    if choice == '1': action = 'overwrite'
                    elif choice == '2': action = 'update'
                    else: action = 'skip'
            
            if action == 'overwrite':
                with open(schema_filename, 'wb') as f: f.write(vdf.binary_dumps(new_schema))
                console.print(f"[green]Successfully overwrote schema file.[/green]")
                summary['overwritten'] += 1
            elif action == 'update':
                with open(schema_filename, 'rb') as f: existing_schema = vdf.binary_load(f)
                merged_schema = deep_merge(new_schema, existing_schema)
                with open(schema_filename, 'wb') as f: f.write(vdf.binary_dumps(merged_schema))
                console.print(f"[green]Successfully updated schema file.[/green]")
                summary['updated'] += 1
            elif action == 'skip':
                console.print("[yellow]Skipped schema file.[/yellow]")
                summary['skipped'] += 1
        else:
            with open(schema_filename, 'wb') as f: f.write(vdf.binary_dumps(new_schema))
            console.print(f"[green]Successfully created new schema file: {os.path.basename(schema_filename)}[/green]")
            summary['updated'] += 1

        stats_dest_filename = os.path.join(DEFAULT_OUTPUT_DIR, f"UserGameStats_{steam_id}_{app_id}.bin")
        if not os.path.exists(stats_dest_filename):
            stats_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'UserGameStats_steamid_appid.bin')
            shutil.copy(stats_template_path, stats_dest_filename)
            console.print(f"[green]Successfully created stats file: {os.path.basename(stats_dest_filename)}[/green]")

        summary['total'] += 1
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            console.print(f"[bold red]Error processing App ID {app_id}: Unauthorized. Your Steam API Key may be invalid.[/bold red]")
        elif e.response.status_code == 404:
            console.print(f"[bold red]Error processing App ID {app_id}: Not Found. The game might not exist or is incorrect.[/bold red]")
        else:
            console.print(f"[bold red]Error processing App ID {app_id}: HTTP Error {e.response.status_code}[/bold red]")
        summary['errors'] += 1
        return False
    except (requests.exceptions.RequestException, KeyError, FileNotFoundError) as e:
        console.print(f"[bold red]Error processing App ID {app_id}: {e}[/bold red]")
        summary['errors'] += 1
        return False

def parse_libraryfolders_vdf():
    """Parse libraryfolders.vdf to extract app IDs"""
    if platform.system() == "Windows":
        STEAM_DIR = Path("C:/Program Files (x86)/Steam")
    else:
        STEAM_DIR = Path.home() / ".local/share/Steam"
    LIBRARY_FILE = STEAM_DIR / "steamapps/libraryfolders.vdf"

    if not LIBRARY_FILE.exists():
        console.print(f"[yellow]Steam library file not found at {LIBRARY_FILE}[/yellow]")
        return []

    console.print(f"Reading Steam library from: [cyan]{LIBRARY_FILE}[/cyan]")
    try:
        with open(LIBRARY_FILE, 'r') as f: data = vdf.load(f)
        app_ids = set()
        for folder_data in data.get('libraryfolders', {}).values():
            if isinstance(folder_data, dict):
                for app_id in folder_data.get('apps', {}).keys():
                    if app_id.isdigit():
                        app_ids.add(int(app_id))
        return sorted(list(app_ids))
    except Exception as e:
        console.print(f"[bold red]Error parsing Steam library file (VDF parse): {e}[/bold red]")
        return []

def get_batch_mode():
    """Gets the batch processing mode from the user."""
    console.print("\n[bold]How do you want to handle existing files?[/bold]")
    console.print("1. Ask for each game (compares for new achievements)")
    console.print("2. Overwrite all")
    console.print("3. Update all (merge new achievements without asking)")
    console.print("4. Generate for new apps only")
    console.print("b. Back to main menu")
    choice = console.input("Select an option: ")
    if choice.lower() == 'b': return 'b'
    if choice == '2': return 'overwrite'
    elif choice == '3': return 'update'
    elif choice == '4': return 'generate_new'
    return 'ask'

def print_summary(summary):
    """Prints a summary of the operations in a table."""
    table = Table(title="[bold]Operation Summary[/bold]")
    table.add_column("Status", style="cyan")
    table.add_column("Count", style="magenta")
    
    table.add_row("Total Games Processed", str(summary['total']))
    table.add_row("Files Updated/Created", str(summary['updated']))
    table.add_row("Files Overwritten", str(summary['overwritten']))
    table.add_row("Files Skipped", str(summary['skipped']))
    if summary['errors'] > 0:
        table.add_row("[bold red]Errors[/bold red]", f"[bold red]{summary['errors']}[/bold red]")
    else:
        table.add_row("Errors", str(summary['errors']))
        
    console.print(table)

def handle_slssteam_list(api_key, steam_id, language):
    clear()
    summary = {'total': 0, 'overwritten': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    try:
        with open(SLSSTEAM_CONFIG_PATH, 'r') as f: config = yaml.safe_load(f)
        app_ids = config.get('AdditionalApps', [])
        if not app_ids:
            console.print("[yellow]No App IDs found in SLSsteam config file.[/yellow]")
            console.input("\nPress Enter to return to the main menu.")
            return

        console.print("[cyan]Checking for app details cache updates...[/cyan]")
        cache = read_cache()
        missing_ids = [app_id for app_id in app_ids if str(app_id) not in cache]
        if missing_ids:
            console.print(f"Found {len(missing_ids)} apps not in cache. Fetching details...")
            cache_modified = False
            for app_id in missing_ids:
                _, modified = get_app_details(app_id, cache)
                if modified: cache_modified = True
            if cache_modified:
                write_cache(cache)
                console.print("[green]Cache updated.[/green]")
        else:
            console.print("[green]App details cache is up to date.[/green]")

        console.print(f"Found {len(app_ids)} App IDs in SLSsteam config.")
        batch_mode = get_batch_mode()
        if batch_mode is None or batch_mode == 'b': return

        with console.status("[bold green]Processing games...[/bold green]") as status:
            for app_id in app_ids:
                status.update(f"Processing App ID: {app_id}")
                if batch_mode == 'generate_new':
                    schema_filename = os.path.join(DEFAULT_OUTPUT_DIR, f"UserGameStatsSchema_{app_id}.bin")
                    if os.path.exists(schema_filename):
                        console.print(f"[yellow]Schema for {app_id} already exists, skipping.[/yellow]")
                        summary['skipped'] += 1
                        continue
                get_game_schema(api_key, steam_id, str(app_id), summary, language, batch_mode if batch_mode != 'generate_new' else 'overwrite')

    except FileNotFoundError:
        console.print(f"[bold red]Error: SLSsteam config file not found at {SLSSTEAM_CONFIG_PATH}[/bold red]")
    except (yaml.YAMLError, Exception) as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
    
    print_summary(summary)
    console.input("\nPress Enter to return to the main menu.")

def handle_steam_library(api_key, steam_id, language):
    clear()
    summary = {'total': 0, 'overwritten': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    app_ids = parse_libraryfolders_vdf()
    if not app_ids:
        console.print("[yellow]No App IDs found in Steam library.[/yellow]")
        console.input("\nPress Enter to return to the main menu.")
        return

    console.print(f"Found {len(app_ids)} App IDs in Steam library.")
    batch_mode = get_batch_mode()
    if batch_mode is None or batch_mode == 'b': return

    with console.status("[bold green]Processing library...[/bold green]") as status:
        for app_id in app_ids:
            status.update(f"Processing App ID: {app_id}")
            get_game_schema(api_key, steam_id, str(app_id), summary, language, batch_mode)

    print_summary(summary)
    console.input("\nPress Enter to return to the main menu.")

def handle_manual_input(api_key, steam_id, language):
    clear()
    summary = {'total': 0, 'overwritten': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    while True:
        app_id = console.input("\nEnter the App ID (or 'b' to return to main menu): ")
        if app_id.lower() == 'b': break
        if not app_id.isdigit():
            console.print("[bold red]Invalid App ID. Please enter a number.[/bold red]")
            continue
        get_game_schema(api_key, steam_id, app_id, summary, language)
    
    if summary['total'] > 0:
        print_summary(summary)
        console.input("\nPress Enter to return to the main menu.")

def handle_sls_manager():
    """Calls the main function of the SLSsteam Config Manager."""
    import sls_manager 
    sls_manager.main()

def handle_clear_credentials():
    clear()
    if os.path.exists(DOTENV_PATH):
        os.remove(DOTENV_PATH)
        console.print("[green]Credentials cleared. Please restart the script to set them up again.[/green]")
    else:
        console.print("[yellow]No credentials found to clear.[/yellow]")
    console.input("\nPress Enter to exit.")

# ... (Rest of the file with console.print replacements) 
def delete_files_for_appids(app_ids, steam_id, source_name):
    """Deletes schema and stats files for a given list of App IDs."""
    if not app_ids:
        console.print(f"[yellow]No App IDs found from {source_name} to purge.[/yellow]")
        return

    files_to_delete = []
    app_ids_found = set()
    for app_id in app_ids:
        app_id_str = str(app_id)
        schema_file = os.path.join(DEFAULT_OUTPUT_DIR, f"UserGameStatsSchema_{app_id_str}.bin")
        stats_file = os.path.join(DEFAULT_OUTPUT_DIR, f"UserGameStats_{steam_id}_{app_id_str}.bin")
        if os.path.exists(schema_file):
            files_to_delete.append(schema_file)
            app_ids_found.add(app_id_str)
        if os.path.exists(stats_file):
            files_to_delete.append(stats_file)
            app_ids_found.add(app_id_str)

    if not files_to_delete:
        console.print(f"[yellow]No generated files found for the App IDs from {source_name}.[/yellow]")
        return

    console.print(f"Found {len(files_to_delete)} file(s) to delete for {len(app_ids_found)} App ID(s) from [cyan]{source_name}[/cyan].")
    console.print("[bold red]This action is irreversible.[/bold red]")
    choice = console.input("Are you sure you want to proceed? (y/n): ").lower()

    if choice != 'y':
        console.print("\n[yellow]Purge operation cancelled.[/yellow]")
        return

    deleted_count = 0
    error_count = 0
    for filepath in files_to_delete:
        try:
            os.remove(filepath)
            deleted_count += 1
        except OSError as e:
            console.print(f"[bold red]Error deleting file {filepath}: {e}[/bold red]")
            error_count += 1
    
    console.print(f"\n[green]Successfully deleted {deleted_count} files.[/green]")
    if error_count > 0:
        console.print(f"[bold red]Failed to delete {error_count} files.[/bold red]")

def handle_purge_manual(steam_id):
    clear()
    console.print("[bold]--- Purge by Manual App ID ---[/bold]")
    app_id_input = console.input("Enter the App ID to purge (or 'b' to go back): ")
    if app_id_input.lower() == 'b': return
    if not app_id_input.isdigit():
        console.print("[bold red]Invalid App ID. Please enter a number.[/bold red]")
    else:
        delete_files_for_appids([app_id_input], steam_id, "manual input")
    console.input("\nPress Enter to continue.")

def handle_purge_slssteam(steam_id):
    clear()
    console.print("[bold]--- Purge from SLSsteam config ---[/bold]")
    try:
        with open(SLSSTEAM_CONFIG_PATH, 'r') as f: config = yaml.safe_load(f)
        app_ids = config.get('AdditionalApps', [])
        if app_ids:
            delete_files_for_appids(app_ids, steam_id, "SLSsteam config")
        else:
            console.print("[yellow]No App IDs found in SLSsteam config file.[/yellow]")
    except FileNotFoundError:
        console.print(f"[bold red]Error: SLSsteam config file not found at {SLSSTEAM_CONFIG_PATH}[/bold red]")
    except (yaml.YAMLError, Exception) as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
    console.input("\nPress Enter to continue.")

def handle_purge_steam_library(steam_id):
    clear()
    console.print("[bold]--- Purge from Steam Library ---[/bold]")
    app_ids = parse_libraryfolders_vdf()
    if app_ids:
        delete_files_for_appids(app_ids, steam_id, "Steam library")
    else:
        console.print("[yellow]Could not find any App IDs in the Steam library.[/yellow]")
    console.input("\nPress Enter to continue.")

def purge_all():
    clear()
    console.print("[bold]--- Purge ALL Generated Schema Files ---[/bold]")

    if not os.path.isdir(DEFAULT_OUTPUT_DIR):
        console.print(f"[yellow]Output directory not found at: {DEFAULT_OUTPUT_DIR}[/yellow]")
        console.input("\nPress Enter to continue.")
        return

    files_to_delete = [os.path.join(DEFAULT_OUTPUT_DIR, f) for f in os.listdir(DEFAULT_OUTPUT_DIR) if (f.startswith("UserGameStatsSchema_") and f.endswith(".bin")) or re.match(r'UserGameStats_(\d+)_(\d+)\.bin', f)]
    if not files_to_delete:
        console.print("[yellow]No generated schema or stats files found to delete.[/yellow]")
        console.input("\nPress Enter to continue.")
        return

    console.print(f"Found {len(files_to_delete)} generated files to delete in [cyan]{DEFAULT_OUTPUT_DIR}[/cyan]")
    console.print("\n[bold red]WARNING: This action is irreversible and will delete ALL generated schema and stats files.[/bold red]")
    choice = console.input("Are you sure you want to proceed? (y/n): ").lower()

    if choice == 'y':
        # ... (deletion logic from before, converted to console.print)
        deleted_count = 0
        error_count = 0
        for filepath in files_to_delete:
            try:
                os.remove(filepath)
                deleted_count += 1
            except OSError as e:
                console.print(f"[bold red]Error deleting file {filepath}: {e}[/bold red]")
                error_count += 1
        console.print(f"\n[green]Successfully deleted {deleted_count} files.[/green]")
        if error_count > 0: console.print(f"[bold red]Failed to delete {error_count} files.[/bold red]")
    else:
        console.print("\n[yellow]Purge operation cancelled.[/yellow]")
    console.input("\nPress Enter to continue.")

def handle_purge_menu(steam_id):
    while True:
        clear()
        console.print("\n[bold]--- Purge Generated Files Menu ---[/bold]")
        console.print("1. Purge by manual App ID")
        console.print("2. Purge based on SLSsteam config")
        console.print("3. Purge based on Steam library")
        console.print("4. Purge ALL generated files")
        console.print("b. Back to main menu")
        choice = console.input("\nSelect an option: ")
        if choice == '1': handle_purge_manual(steam_id)
        elif choice == '2': handle_purge_slssteam(steam_id)
        elif choice == '3': handle_purge_steam_library(steam_id)
        elif choice == '4': purge_all()
        elif choice.lower() == 'b': break
        else: console.print("[bold red]Invalid option.[/bold red]"); console.input()

def handle_update():
    clear()
    console.print("[bold cyan]Updating...[/bold cyan]")
    os.system("bash install.sh")
    console.print("\n[bold green]Update complete. Please restart the script.[/bold green]")
    console.input("Press Enter to exit.")

def handle_uninstall():
    clear()
    os.system("bash uninstall.sh")
    console.input("\nPress Enter to exit.")

def main():
    """Main function of the script."""
    if not check_internet_connection(): sys.exit(1)
    load_dotenv(dotenv_path=DOTENV_PATH)
    api_key = os.getenv("STEAM_API_KEY")
    steam_id = os.getenv("STEAM_USER_ID")
    language = 'english' # Keep for API calls, but not user-changeable
    if not api_key or not steam_id:
        clear()
        api_key = get_env_value("STEAM_API_KEY", "Steam API Key", "https://steamcommunity.com/dev/apikey")
        steam_id = get_env_value("STEAM_USER_ID", "Steam User ID", "https://steamid.io/", "[U:1:xxxxxxxxx]")

    # Re-numbered and cleaned up menu items
    menu_items = {
        '-- Generation --': [
            ('1', 'Generate from SLSsteam config', handle_slssteam_list),
            ('2', 'Scan Steam library for games', handle_steam_library),
            ('3', 'Manual App ID input', handle_manual_input),
        ],
        '-- Management --': [
            ('4', 'Manage SLSsteam App List', handle_sls_manager),
            ('5', 'Purge generated schemas', handle_purge_menu),
        ],
        '-- Settings --': [
            ('6', 'Clear Credentials', handle_clear_credentials),
        ],
        '-- Application --': [
            ('7', 'Update', handle_update),
            ('8', 'Uninstall', handle_uninstall),
        ]
    }
    
    all_options = {key: handler for group in menu_items.values() for key, _, handler in group}

    while True:
        clear()
        console.print(f"[bold]--- Steam Achievement Helper ---[/bold]\n")

        for header, items in menu_items.items():
            console.print(f"  [bold cyan]{header}[/bold cyan]")
            for key, text, _ in items:
                console.print(f"  [yellow]{key}[/yellow]. {text}")
            console.print() # Spacer

        choice = console.input("Select an option ('q' for quit): ")

        if choice.lower() == 'q': break

        if choice in all_options:
            handler = all_options[choice]
            # Corrected handler calls
            if choice in ['1', '2', '3']:
                handler(api_key, steam_id, language)
            elif choice == '5':
                handler(steam_id) # Purge menu needs steam_id
            elif choice in ['4', '6', '7', '8']:
                handler()
                if choice in ['6', '7', '8']: break # Exit after these actions
            else:
                # This case should ideally not be reached with the current structure
                console.print("[bold red]Internal error: Unhandled option.[/bold red]")
                console.input("\nPress Enter to continue.")
        else:
            console.print("[bold red]Invalid option.[/bold red]")
            console.input("\nPress Enter to continue.")

if __name__ == '__main__':
    main()
