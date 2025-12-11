import os
import json
import requests
import re
from dotenv import load_dotenv, set_key
from rich.console import Console

console = Console()

CACHE_FILE_PATH = os.path.expanduser("~/.config/SLSsteam/appinfo_cache.json")
DOTENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

def get_env_value(key, prompt, help_url="", example=""):
    """Gets a value from the .env file, or prompts the user for it if it doesn't exist."""
    load_dotenv(dotenv_path=DOTENV_PATH)
    value = os.getenv(key)

    while not value:
        console.print(f"\n[yellow]{prompt} not found.[/yellow]")
        if help_url:
            console.print(f"You can get one from: [cyan]{help_url}[/cyan]")
        if example:
            console.print(f"Example format: [dim]{example}[/dim]")
            
        value = console.input(f"Please enter your [bold yellow]{prompt}[/bold yellow]: ").strip()

        if not value:
            console.print("[bold red]Input cannot be empty.[/bold red]")
            continue

        if key == "STEAM_API_KEY":
            if not re.match(r'^[a-fA-F0-9]{32}$', value):
                console.print("[bold red]Invalid API Key format. It should be a 32-character hexadecimal string.[/bold red]")
                value = None
                continue

        if key == "STEAM_USER_ID":
            match = re.search(r'(\d+)]?$', value)
            if match:
                value = match.group(1)
        
        # Ensure .env file exists before writing
        if not os.path.exists(DOTENV_PATH):
            open(DOTENV_PATH, 'a').close()

        set_key(DOTENV_PATH, key, value)
        console.print(f"[green]{prompt} saved to .env file.[/green]")

    return value

def read_cache():
    """Reads the app details cache file."""
    if not os.path.exists(CACHE_FILE_PATH):
        return {}
    try:
        with open(CACHE_FILE_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Warning: Could not read cache file. A new one will be created. Error: {e}")
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
