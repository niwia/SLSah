import yaml
import os
import sys
import re
import platform
import requests
import shutil
import json
import time
from datetime import datetime

# Import the generator script to use its functions
import generate_schema_from_api as achievement_generator
from shared_utils import read_cache, write_cache, get_app_details, CACHE_FILE_PATH

# --- Constants ---
SLSSTEAM_CONFIG_PATH = os.path.expanduser("~/.config/SLSsteam/config.yaml")
BACKUP_DIR = os.path.expanduser("~/.config/SLSsteam/backup")

# --- Basic Functions ---
def clear():
    """Clears the console screen."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# --- Helper Functions ---
def read_config():
    try:
        with open(SLSSTEAM_CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            if config and 'AdditionalApps' in config and config['AdditionalApps'] is not None:
                return config['AdditionalApps']
    except FileNotFoundError:
        return []
    except (yaml.YAMLError, Exception) as e:
        print(f"Error reading or parsing YAML file: {e}")
        return None
    return []

def write_config(app_ids):
    """
    Writes the list of app_ids to the 'AdditionalApps' section of the config file,
    preserving comments and other values in the file.
    """
    try:
        try:
            with open(SLSSTEAM_CONFIG_PATH, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        if not lines:
            lines = [
                "#Additional AppIds to inject (Overrides your black-/whitelist & also overrides OwnerIds for apps you got shared!) Best to use this only on games NOT in your library.\n",
                "AdditionalApps:\n"
            ]

        # Find start of the AdditionalApps list
        start_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("AdditionalApps:"):
                start_index = i
                break
        
        if start_index == -1:
            # If not found, add it at the end, ensuring there's a newline before it
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append("\n#Additional AppIds to inject (Overrides your black-/whitelist & also overrides OwnerIds for apps you got shared!) Best to use this only on games NOT in your library.\n")
            lines.append("AdditionalApps:\n")
            start_index = len(lines) - 1

        indent_level = lines[start_index].find("AdditionalApps:")
        
        # Create the new list of app ID lines
        new_list_item_lines = []
        for app_id in sorted(list(set(app_ids))):
            # Format: indent, space, hyphen, space, appid
            new_list_item_lines.append(' ' * (indent_level + 1) + f'- {app_id}\n')

        # Find end of the old list
        end_index = start_index + 1
        while end_index < len(lines):
            line = lines[end_index]
            # A list item is indented and starts with '-'
            is_list_item = line.strip().startswith('-') and (len(line) - len(line.lstrip(' '))) > indent_level
            if not is_list_item:
                break
            end_index += 1
            
        # Reconstruct the file content
        final_lines = lines[:start_index + 1] + new_list_item_lines + lines[end_index:]

        os.makedirs(os.path.dirname(SLSSTEAM_CONFIG_PATH), exist_ok=True)
        with open(SLSSTEAM_CONFIG_PATH, 'w') as f:
            f.writelines(final_lines)
        
        return True

    except Exception as e:
        print(f"An error occurred during file write: {e}")
        return False

def backup_config():
    if not os.path.exists(SLSSTEAM_CONFIG_PATH):
        return True
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True) # Ensure backup dir exists
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"config.{timestamp}.yaml")
        shutil.copy(SLSSTEAM_CONFIG_PATH, backup_file)
        backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith('config.')], key=os.path.getmtime, reverse=True)
        if len(backups) > 10:
            for old_backup in backups[10:]:
                os.remove(old_backup)
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def get_all_app_details(cache):
    app_ids = read_config()
    if app_ids is None:
        return None, False
    
    app_details_list = []
    cache_modified = False
    total_apps = len(app_ids)
    if total_apps > 0:
        print(f"Found {total_apps} apps. Fetching details...")

    for i, app_id in enumerate(app_ids):
        print(f"\r[{i+1}/{total_apps}] Fetching details for {app_id}...", end="")
        details, modified = get_app_details(app_id, cache)
        if modified:
            cache_modified = True
        app_details_list.append({'id': app_id, 'name': details['name'] if details else 'Unknown App', 'type': details['type'] if details else 'unknown'})
    
    if total_apps > 0:
        print("\r" + " " * 60 + "\r", end="") # Clear line
    return app_details_list, cache_modified

def inform_manual_restart():
    print("\nChanges saved. Please restart Steam manually for them to take effect.")

# --- Main Application Logic ---
def handle_list_games(cache):
    """Returns a status string: 'back', 'main_menu', or cache_modified status."""
    while True:
        clear()
        print("--- Managed Games & DLCs ---")
        app_details_list, cache_modified = get_all_app_details(cache)

        if app_details_list is None:
            input("\nPress Enter to continue.")
            return 'back'
        if not app_details_list:
            print("No apps found in the SLSsteam config file.")
        else:
            games, dlcs, others = [], [], []
            for app in app_details_list:
                display_name = f"{app['name']} ({app['id']})"
                if app['type'] == 'game':
                    games.append(display_name)
                elif app['type'] == 'dlc':
                    dlcs.append(display_name)
                else:
                    others.append(display_name)

            if games:
                print("\n--- Games ---")
                for game in sorted(games):
                    print(f"- {game}")
            if dlcs:
                print("\n--- DLCs ---")
                for dlc in sorted(dlcs):
                    print(f"- {dlc}")
            if others:
                print("\n--- Other/Unknown ---")
                for other in sorted(others):
                    print(f"- {other}")
        
        # --- FIX: Added (m)ain menu to prompt ---
        choice = input("\n(r)efresh, (b)ack, (m)ain menu: ").lower()
        if choice == 'r':
            print("Refreshing...")
            continue
        elif choice == 'm':
            return "main_menu"
        else: # Default to back
            return cache_modified

def handle_add_game(cache):
    cache_modified_in_session = False
    while True:
        clear()
        print("--- Add a New App/DLC ---")
        app_id_input = input("Enter App ID(s) (b: back, m: main menu): ").strip()
        if app_id_input.lower() == 'b':
            return cache_modified_in_session
        if app_id_input.lower() == 'm':
            return "main_menu"
        
        id_strings = [id_str.strip() for id_str in app_id_input.replace(',', ' ').split()]
        if not id_strings:
            print("No App IDs entered.")
            input("\nPress Enter to continue.")
            continue

        app_ids_to_add = []
        for id_str in id_strings:
            if not id_str.isdigit():
                print(f"Skipping invalid input: '{id_str}'")
                continue
            app_ids_to_add.append(int(id_str))

        if not app_ids_to_add:
            print("No valid App IDs to add.")
            input("\nPress Enter to continue.")
            continue

        current_app_ids = read_config()
        if current_app_ids is None:
            input("\nPress Enter to continue.")
            continue

        existing_app_ids = [id for id in app_ids_to_add if id in current_app_ids]
        new_app_ids = [id for id in app_ids_to_add if id not in current_app_ids]

        if existing_app_ids:
            print(f"\nThe following App IDs are already in the config and will be skipped: {', '.join(map(str, existing_app_ids))}")

        if not new_app_ids:
            print("No new App IDs to add.")
            input("\nPress Enter to continue.")
            continue

        print(f"Fetching details for {len(new_app_ids)} new app(s)...")
        apps_to_confirm = []
        cache_modified_this_round = False
        for app_id in new_app_ids:
            details, modified = get_app_details(app_id, cache)
            if modified:
                cache_modified_in_session = True
                cache_modified_this_round = True
            apps_to_confirm.append({'id': app_id, 'details': details})

        print("\nYou are about to add the following:")
        for app in apps_to_confirm:
            if app['details']:
                print(f"- {app['details']['name']} ({app['id']}) - Type: {app['details']['type']}")
            else:
                print(f"- Unknown App ({app['id']})")

        if input("\nProceed with adding these apps? (y/n): ").lower() != 'y':
            print("Add operation cancelled.")
            input("\nPress Enter to continue.")
            continue

        if not backup_config():
            input("\nPress Enter to continue.")
            continue

        final_app_list = current_app_ids + new_app_ids
        if write_config(final_app_list):
            print(f"\nSuccessfully added {len(new_app_ids)} app(s) to the config file.")
            if input("Generate achievement schemas for the new apps now? (y/n): ").lower() == 'y':
                api_key = achievement_generator.get_env_value("STEAM_API_KEY", "Steam API Key", "https://steamcommunity.com/dev/apikey")
                steam_id = achievement_generator.get_env_value("STEAM_USER_ID", "Steam User ID", "https://steamid.io/", "[U:1:xxxxxxxxx]")
                batch_mode = achievement_generator.get_batch_mode()
                if batch_mode and batch_mode != 'b':
                    summary = {'total': 0, 'errors': 0, 'skipped': 0, 'updated': 0, 'overwritten': 0}
                    for app_id in new_app_ids:
                        achievement_generator.get_game_schema(api_key, steam_id, str(app_id), summary, 'english', batch_mode)
                    achievement_generator.print_summary(summary)

            inform_manual_restart()
        else:
            print("Failed to write to config file. Add operation cancelled.")
        
        input("\nPress Enter to add more apps, or 'b' to go back.")
        # --- FIX: Changed return value to correctly propagate cache status ---
        return cache_modified_in_session or cache_modified_this_round

def handle_remove_game(cache):
    cache_modified_in_session = False
    while True:
        clear()
        print("--- Remove an App ---")
        app_details_list, cache_modified = get_all_app_details(cache)
        if cache_modified:
            cache_modified_in_session = True

        if app_details_list is None:
            input("\nPress Enter to continue.")
            return False
        if not app_details_list:
            print("No apps found in the SLSsteam config file to remove.")
            input("\nPress Enter to continue.")
            return cache_modified_in_session

        app_details_list.sort(key=lambda x: x['name'])
        print("\nWhich app do you want to remove?")
        for i, details in enumerate(app_details_list):
            print(f"{i + 1}. {details['name']} ({details['id']}) - [{details['type']}]")
        
        choice = input("\nSelect an option (b: back, m: main menu): ").strip()
        if choice.lower() == 'b':
            return cache_modified_in_session
        if choice.lower() == 'm':
            return "main_menu"

        try:
            choice_index = int(choice) - 1
            if not 0 <= choice_index < len(app_details_list):
                raise ValueError
            app_to_remove = app_details_list[choice_index]
            app_id_to_remove = app_to_remove['id']
            if input(f"Remove {app_to_remove['name']} ({app_id_to_remove}) from the config? (y/n): ").lower() == 'y':
                if not backup_config():
                    input("\nPress Enter to continue.")
                    continue
                
                current_app_ids = [app['id'] for app in app_details_list]
                current_app_ids.remove(app_id_to_remove)

                if write_config(current_app_ids):
                    print(f"Successfully removed {app_id_to_remove} from the config file.")
                    if input(f"Delete generated files for {app_id_to_remove}? (y/n): ").lower() == 'y':
                        steam_id = achievement_generator.get_env_value("STEAM_USER_ID", "Steam User ID", "https://steamid.io/", "[U:1:xxxxxxxxx]")
                        print("Attempting to delete files...")
                        # --- FIX: Pass steam_id as a string ---
                        achievement_generator.delete_files_for_appids([app_id_to_remove], str(steam_id), f"app {app_id_to_remove}")
                    
                    print("\nReminder: Don't forget to manually uninstall the game from Steam")
                    print("and delete any remaining game files if desired.")
                    inform_manual_restart()
                else:
                    print("Failed to write to config file.")
            else:
                print("Remove operation cancelled.")
            input("\nPress Enter to continue.")
        except ValueError:
            print("Invalid selection.")
            time.sleep(2)
            continue

def handle_restore_backup():
    clear()
    print("--- Restore a Backup ---")
    try:
        backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('config.') and f.endswith('.yaml')], reverse=True)
    except FileNotFoundError:
        print(f"Backup directory not found at: {BACKUP_DIR}")
        input("\nPress Enter to continue.")
        return
    if not backups:
        print("No backups found.")
        input("\nPress Enter to continue.")
        return
    print("Available backups (most recent first):\n")
    for i, backup_name in enumerate(backups):
        try:
            timestamp_str = backup_name.replace('config.', '').replace('.yaml', '')
            dt_obj = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
            print(f"{i + 1}. {dt_obj.strftime('%Y-%m-%d %H:%M:%S')}")
        except ValueError:
            print(f"{i + 1}. {backup_name} (unrecognized format)")

    choice = input("\nSelect a backup to restore (b: back, m: main menu): ").strip()
    if choice.lower() == 'b':
        return
    if choice.lower() == 'm':
        return "main_menu"

    try:
        choice_index = int(choice) - 1
        if not 0 <= choice_index < len(backups):
            raise ValueError
        backup_to_restore = backups[choice_index]
        if input(f"Overwrite current config with backup from {backup_to_restore}? (y/n): ").lower() == 'y':
            backup_path = os.path.join(BACKUP_DIR, backup_to_restore)
            shutil.copy(backup_path, SLSSTEAM_CONFIG_PATH)
            print("\nSuccessfully restored the config file.")
        else:
            print("\nRestore operation cancelled.")
    except ValueError:
        print("Invalid selection.")
    input("\nPress Enter to continue.")

def handle_clear_cache():
    """Clears the app info cache."""
    clear()
    print("--- Clear App Details Cache ---")
    if os.path.exists(CACHE_FILE_PATH):
        if input("Are you sure you want to delete the cache file? (y/n): ").lower() == 'y':
            try:
                os.remove(CACHE_FILE_PATH)
                print("Cache cleared.")
            except OSError as e:
                print(f"Error deleting cache file: {e}")
        else:
            print("Operation cancelled.")
    else:
        print("No cache file found to clear.")
    input("\nPress Enter to continue.")

def main():
    """Main function for the SLSsteam Manager."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    cache = read_cache()
    cache_modified = False

    while True:
        clear()
        print("\n--- SLSsteam Config Manager ---")
        print()
        print("1. List Managed Games & DLCs")
        print("2. Add a New App/DLC")
        print("3. Remove an App")
        print("4. Restore a Backup")
        print("5. Clear App Details Cache")
        print("m. Back to Main Menu")
        choice = input("\nSelect an option: ")

        result = False
        if choice == '1':
            result = handle_list_games(cache)
        elif choice == '2':
            result = handle_add_game(cache)
        elif choice == '3':
            result = handle_remove_game(cache)
        elif choice == '4':
            result = handle_restore_backup()
        elif choice == '5':
            handle_clear_cache()
        elif choice.lower() == 'm' or choice.lower() == 'q':
            break
        else:
            print("Invalid option.")
            input("\nPress Enter to continue.")
        
        if result == "main_menu":
            break
        
        if result is True:
            cache_modified = True
    
    if cache_modified:
        print("Saving app details to cache...")
        write_cache(cache)

if __name__ == '__main__':
    main()