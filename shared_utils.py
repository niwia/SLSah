import os
import json
import requests

CACHE_FILE_PATH = os.path.expanduser("~/.config/SLSsteam/appinfo_cache.json")

def read_cache():
    """Reads the app details cache file."""
    if not os.path.exists(CACHE_FILE_PATH):
        # --- FIX: Changed {{}} to {} ---
        return {}
    try:
        with open(CACHE_FILE_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Could not read cache file. A new one will be created. Error: {e}")
        # --- FIX: Changed {{}} to {} ---
        return {}

def write_cache(cache_data):
    """Writes data to the app details cache file."""
    try:
        os.makedirs(os.path.dirname(CACHE_FILE_PATH), exist_ok=True)
        with open(CACHE_FILE_PATH, 'w') as f:
            json.dump(cache_data, f, indent=4)
    except Exception as e:
        print(f"Warning: Could not write to cache file. Error: {e}")

def get_app_details(app_id, cache):
    """Fetches app details from API if not in cache. Returns (details, modified_flag)."""
    app_id_str = str(app_id)
    if app_id_str in cache:
        return cache[app_id_str], False
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if app_id_str in data and data[app_id_str]['success']:
            app_data = data[app_id_str]['data']
            details = {'name': app_data.get('name', 'Unknown Name'), 'type': app_data.get('type', 'unknown')}
            cache[app_id_str] = details
            return details, True
    except requests.exceptions.RequestException as e:
        # This is a soft failure, we don't want to interrupt the user for one failed lookup
        print(f"\nWarning: Could not fetch details for App ID {app_id}. Error: {e}")
    return None, False