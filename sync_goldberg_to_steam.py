
import os
import platform
import vdf
import configparser
import time
import sys

def get_goldberg_save_path():
    """Returns the platform-specific path to Goldberg saves."""
    if platform.system() == "Windows":
        appdata = os.getenv('APPDATA')
        if appdata:
            return os.path.join(appdata, "Goldberg SteamEmu Saves")
    # For Linux, the path is often in ~/.steam/steam/
    # but Goldberg can be configured differently. We'll assume a common default.
    return os.path.expanduser("~/.steam/steam/goldberg_saves")

def get_steam_stats_path():
    """Returns the platform-specific path to Steam's stats directory."""
    if platform.system() == "Windows":
        # This path can vary based on Steam installation, but this is a common default
        program_files = os.environ.get("ProgramFiles(x86)", os.environ.get("ProgramFiles"))
        if program_files:
            return os.path.join(program_files, "Steam", "appcache", "stats")
    # Default for Linux/macOS
    return os.path.expanduser("~/.steam/steam/appcache/stats")

def sync_achievements(app_id, steam_id):
    """
    Syncs unlocked achievements from Goldberg Emulator to the official Steam .bin file.
    """
    print(f"--- Starting sync for App ID: {app_id} and Steam ID: {steam_id} ---")

    # --- 1. Find and parse Goldberg achievement file ---
    goldberg_path = get_goldberg_save_path()
    goldberg_ach_file = os.path.join(goldberg_path, str(app_id), "achiev.ini")

    if not os.path.exists(goldberg_ach_file):
        print(f"Error: Goldberg achievement file not found at {goldberg_ach_file}")
        return

    print(f"Found Goldberg achievement file: {goldberg_ach_file}")
    config = configparser.ConfigParser()
    config.read(goldberg_ach_file)

    goldberg_unlocked = set()
    if 'Achievements' in config:
        for ach_name in config['Achievements']:
            if config['Achievements'][ach_name] == '1':
                goldberg_unlocked.add(ach_name.upper())
    
    if not goldberg_unlocked:
        print("No achievements found as unlocked in Goldberg file. Nothing to sync.")
        return
    
    print(f"Found {len(goldberg_unlocked)} unlocked achievements in Goldberg file.")

    # --- 2. Find and parse Steam .bin file ---
    steam_stats_path = get_steam_stats_path()
    steam_bin_file = os.path.join(steam_stats_path, f"UserGameStats_{steam_id}_{app_id}.bin")

    if not os.path.exists(steam_bin_file):
        print(f"Error: Steam stats file not found at {steam_bin_file}")
        print("Please ensure the game has been run at least once via Steam to generate this file.")
        return

    print(f"Found Steam stats file: {steam_bin_file}")
    with open(steam_bin_file, 'rb') as f:
        steam_data = vdf.binary_load(f)

    # The data is nested under the app_id as a string
    app_id_str = str(app_id)
    if app_id_str not in steam_data:
        print(f"Error: AppID {app_id} not found inside the Steam .bin file.")
        return

    # --- 3. Compare and merge ---
    achievements_updated = 0
    # Navigate to the achievements section. The structure might vary, but this is common.
    try:
        stats_data = steam_data[app_id_str]['Stats']
        for key, ach_data in stats_data.items():
            if 'name' in ach_data and ach_data['name'].upper() in goldberg_unlocked:
                if ach_data.get('unlock_time', 0) == 0:
                    print(f"  - Syncing achievement: {ach_data['name']}")
                    ach_data['unlock_time'] = int(time.time())
                    achievements_updated += 1
    except KeyError:
        print("Error: Could not find 'Stats' section in the .bin file. The file format may be unexpected.")
        return

    # --- 4. Write updated .bin file ---
    if achievements_updated > 0:
        print(f"Updated {achievements_updated} achievements. Writing changes to .bin file...")
        try:
            with open(steam_bin_file, 'wb') as f:
                f.write(vdf.binary_dumps(steam_data))
            print("Successfully synced achievements!")
        except Exception as e:
            print(f"Error writing to .bin file: {e}")
    else:
        print("All achievements are already in sync.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python sync_goldberg_to_steam.py <app_id> <steam_id>")
        sys.exit(1)
    
    app_id = sys.argv[1]
    steam_id = sys.argv[2]

    if not app_id.isdigit() or not steam_id.isdigit():
        print("Error: App ID and Steam ID must be numeric.")
        sys.exit(1)

    sync_achievements(app_id, steam_id)

if __name__ == "__main__":
    main()
