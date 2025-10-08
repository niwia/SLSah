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

DOTENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.steam/steam/appcache/stats")
SLSSTEAM_CONFIG_PATH = os.path.expanduser("~/.config/SLSsteam/config.yaml")

def get_env_value(key, prompt, help_url="", example=""):
    load_dotenv(dotenv_path=DOTENV_PATH)
    value = os.getenv(key)

    while not value:
        print(f"\n{prompt} not found.")
        if help_url:
            print(f"You can get one from: {help_url}")
        if example:
            print(f"Example format: {example}")
            
        value = input(f"Please enter your {prompt}: ")

        if key == "STEAM_API_KEY" and len(value) < 20:
            print("Invalid API Key. It should be at least 20 characters long.")
            value = None
            continue

        set_key(DOTENV_PATH, key, value)
        print(f"{prompt} saved to .env file.")

    return value

def deep_merge(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            destination[key] = value
    return destination

def get_game_schema(api_key, steam_id, app_id, summary, batch_mode='ask'):
    try:
        url = f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={api_key}&appid={app_id}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        game_name = data['game']['gameName']
        print(f"--- Processing {game_name} ({app_id}) ---")

        new_schema = {
            app_id: {
                "gamename": game_name,
                "version": data['game']['gameVersion'],
                "stats": {"1": {"type": "4", "id": "1", "bits": {}}}
            }
        }
        if 'availableGameStats' in data['game'] and 'achievements' in data['game']['availableGameStats']:
            for i, ach in enumerate(data['game']['availableGameStats']['achievements']):
                new_schema[app_id]["stats"]["1"]["bits"][str(i)] = {
                    "name": ach['name'], "bit": i,
                    "display": {
                        "name": {"english": ach['displayName'], "token": f"NEW_ACHIEVEMENT_1_{i}_NAME"},
                        "desc": {"english": ach.get('description', ''), "token": f"NEW_ACHIEVEMENT_1_{i}_DESC"},
                        "hidden": str(ach['hidden']), "icon": ach['icon'].split('/')[-1], "icon_gray": ach['icongray'].split('/')[-1]
                    }
                }
        
        if not os.path.exists(DEFAULT_OUTPUT_DIR):
            os.makedirs(DEFAULT_OUTPUT_DIR)
            
        schema_filename = os.path.join(DEFAULT_OUTPUT_DIR, f"UserGameStatsSchema_{app_id}.bin")
        action = batch_mode
        if batch_mode == 'ask' and os.path.exists(schema_filename):
            choice = input(f"'{os.path.basename(schema_filename)}' already exists. [1] Overwrite, [2] Update, [3] Skip? ")
            if choice == '1': action = 'overwrite'
            elif choice == '2': action = 'update'
            else: action = 'skip'

        if action == 'overwrite':
            with open(schema_filename, 'wb') as f: f.write(vdf.binary_dumps(new_schema))
            print(f"Successfully overwrote schema file.")
            summary['overwritten'] += 1
        elif action == 'update':
            if not os.path.exists(schema_filename):
                with open(schema_filename, 'wb') as f: f.write(vdf.binary_dumps(new_schema))
                print(f"Successfully saved schema file: {os.path.basename(schema_filename)}")
                summary['updated'] += 1
            else:
                with open(schema_filename, 'rb') as f: existing_schema = vdf.binary_load(f)
                merged_schema = deep_merge(new_schema, existing_schema)
                with open(schema_filename, 'wb') as f: f.write(vdf.binary_dumps(merged_schema))
                print(f"Successfully updated schema file.")
                summary['updated'] += 1
        elif action != 'skip':
             with open(schema_filename, 'wb') as f: f.write(vdf.binary_dumps(new_schema))
             print(f"Successfully saved schema file: {os.path.basename(schema_filename)}")

        if action == 'skip':
            print("Skipped schema file.")
            summary['skipped'] += 1

        stats_dest_filename = os.path.join(DEFAULT_OUTPUT_DIR, f"UserGameStats_{steam_id}_{app_id}.bin")
        if not os.path.exists(stats_dest_filename):
            stats_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'UserGameStats_steamid_appid.bin')
            shutil.copy(stats_template_path, stats_dest_filename)
            print(f"Successfully created stats file: {os.path.basename(stats_dest_filename)}")

        summary['total'] += 1
        return True

    except (requests.exceptions.RequestException, KeyError, FileNotFoundError) as e:
        print(f"Error processing App ID {app_id}: {e}")
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
        print(f"Steam library file not found at {LIBRARY_FILE}")
        return []

    print(f"Reading Steam library from: {LIBRARY_FILE}")
    content = LIBRARY_FILE.read_text()

    app_ids = set(re.findall(r'"apps"\s*{([^}]+)}', content, re.DOTALL))
    app_ids = set(re.findall(r'"(\d+)"\s*"', ''.join(app_ids)))

    return sorted([int(app_id) for app_id in app_ids if app_id.isdigit()])

def process_steam_library(api_key, steam_id):
    summary = {'total': 0, 'overwritten': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    app_ids = parse_libraryfolders_vdf()
    if not app_ids:
        print("No App IDs found in Steam library.")
        return

    print(f"Found {len(app_ids)} App IDs in Steam library.")
    print("\nHow do you want to handle existing files?")
    print("1. Ask for each game")
    print("2. Overwrite all")
    print("3. Update all")
    print("4. Skip all")
    print("b. Back to main menu")
    choice = input("Select an option: ")
    batch_mode = 'ask'
    if choice.lower() == 'b':
        return
    if choice == '2': batch_mode = 'overwrite'
    elif choice == '3': batch_mode = 'update'
    elif choice == '4': batch_mode = 'skip'

    for app_id in app_ids:
        get_game_schema(api_key, steam_id, str(app_id), summary, batch_mode)

    print("\n--- Summary ---")
    print(f"Total games processed: {summary['total']}")
    print(f"Files overwritten: {summary['overwritten']}")
    print(f"Files updated: {summary['updated']}")
    print(f"Files skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")

def process_slssteam_list(api_key, steam_id):
    summary = {'total': 0, 'overwritten': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    try:
        with open(SLSSTEAM_CONFIG_PATH, 'r') as f: config = yaml.safe_load(f)
        app_ids = config.get('AdditionalApps', [])
        if not app_ids:
            print("No App IDs found in SLSsteam config file.")
            return

        print(f"Found {len(app_ids)} App IDs in SLSsteam config.")
        print("\nHow do you want to handle existing files?")
        print("1. Ask for each game")
        print("2. Overwrite all")
        print("3. Update all")
        print("4. Skip all")
        print("b. Back to main menu")
        choice = input("Select an option: ")
        if choice.lower() == 'b':
            return
        batch_mode = 'ask'
        if choice == '2': batch_mode = 'overwrite'
        elif choice == '3': batch_mode = 'update'
        elif choice == '4': batch_mode = 'skip'

        for app_id in app_ids:
            get_game_schema(api_key, steam_id, str(app_id), summary, batch_mode)

    except FileNotFoundError:
        print(f"Error: SLSsteam config file not found at {SLSSTEAM_CONFIG_PATH}")
    except Exception as e:
        print(f"An error occurred while processing the SLSsteam config file: {e}")
    
    print("\n--- Summary ---")
    print(f"Total games processed: {summary['total']}")
    print(f"Files overwritten: {summary['overwritten']}")
    print(f"Files updated: {summary['updated']}")
    print(f"Files skipped: {summary['skipped']}")
    print(f"Errors: {summary['errors']}")

def manual_input_mode(api_key, steam_id):
    summary = {'total': 0, 'overwritten': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    while True:
        app_id = input("\nEnter the App ID (or 'b' to return to main menu): ")
        if app_id.lower() == 'b': break
        if not app_id.isdigit():
            print("Invalid App ID. Please enter a number.")
            continue
        get_game_schema(api_key, steam_id, app_id, summary)
    if summary['total'] > 0:
        print("\n--- Summary ---")
        print(f"Total games processed: {summary['total']}")
        print(f"Files overwritten: {summary['overwritten']}")
        print(f"Files updated: {summary['updated']}")
        print(f"Files skipped: {summary['skipped']}")
        print(f"Errors: {summary['errors']}")

def clear_credentials():
    if os.path.exists(DOTENV_PATH):
        os.remove(DOTENV_PATH)
        print("Credentials cleared. Please restart the script to set them up again.")
    else:
        print("No credentials found to clear.")

def main():
    load_dotenv(dotenv_path=DOTENV_PATH)
    api_key = os.getenv("STEAM_API_KEY")
    steam_id = os.getenv("STEAM_USER_ID")

    if not api_key or not steam_id:
        api_key = get_env_value("STEAM_API_KEY", "Steam API Key", "https://steamcommunity.com/dev/apikey")
        steam_id = get_env_value("STEAM_USER_ID", "Steam User ID", "https://steamid.io/", "[U:1:xxxxxxxxx]")

    while True:
        print("\n--- Steam Schema Generator ---")
        print("1. Generate from SLSsteam config")
        print("2. Scan Steam library for games")
        print("3. Manual App ID input")
        print("4. Clear Credentials")
        print("q. Quit")
        choice = input("Select an option: ")

        if choice == '1':
            process_slssteam_list(api_key, steam_id)
        elif choice == '2':
            process_steam_library(api_key, steam_id)
        elif choice == '3':
            manual_input_mode(api_key, steam_id)
        elif choice == '4':
            clear_credentials()
            break
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
    main()