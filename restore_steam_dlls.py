
import os
import platform
import vdf
import shutil
import sys

def find_steam_install_path():
    """Finds the root directory of the Steam installation."""
    if platform.system() == "Windows":
        import winreg
        try:
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\WOW6432Node\Valve\Steam")
            return winreg.QueryValueEx(hkey, "InstallPath")[0]
        except FileNotFoundError:
            return os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Steam")
    elif platform.system() == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Steam")
    else: # Linux
        return os.path.expanduser("~/.steam/steam")

def find_steam_library_folders(steam_path):
    """Parses libraryfolders.vdf to find all Steam library paths."""
    library_folders_vdf = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
    libraries = [steam_path] # The main install dir is always a library
    if not os.path.exists(library_folders_vdf):
        return libraries

    with open(library_folders_vdf, 'r') as f:
        data = vdf.load(f)
    
    for key, value in data.get('libraryfolders', {}).items():
        if key.isdigit() and 'path' in value:
            libraries.append(value['path'])
            
    return libraries

def find_game_install_path(libraries, app_id):
    """Finds the installation path for a given App ID."""
    app_manifest_file = f"appmanifest_{app_id}.acf"
    for library_path in libraries:
        manifest_path = os.path.join(library_path, 'steamapps', app_manifest_file)
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                data = vdf.load(f)
            install_dir = data.get('AppState', {}).get('installdir')
            if install_dir:
                return os.path.join(library_path, 'steamapps', 'common', install_dir)
    return None

def restore_dlls(game_path, steam_path):
    """Restores the original Steam API DLLs in the given game path."""
    print(f"\nScanning for Steam API DLLs in: {game_path}")
    original_dlls = {
        "steam_api.dll": os.path.join(steam_path, "steam_api.dll"),
        "steam_api64.dll": os.path.join(steam_path, "steam_api64.dll")
    }
    found_and_restored = False

    for dll_name, original_dll_path in original_dlls.items():
        game_dll_path = os.path.join(game_path, dll_name)
        if os.path.exists(game_dll_path):
            # Compare file sizes as a simple check
            if os.path.getsize(game_dll_path) != os.path.getsize(original_dll_path):
                print(f"  - Found modified '{dll_name}'.")
                try:
                    # Backup the modified DLL
                    backup_path = f"{game_dll_path}.bak"
                    print(f"    - Backing up to {backup_path}")
                    shutil.move(game_dll_path, backup_path)
                    
                    # Copy the original DLL
                    print(f"    - Restoring original from {steam_path}")
                    shutil.copy(original_dll_path, game_dll_path)
                    print("    - Restore successful.")
                    found_and_restored = True
                except Exception as e:
                    print(f"    - Error: Failed to restore {dll_name}. {e}")
            else:
                print(f"  - Found '{dll_name}'. It appears to be original (same size). Skipping.")

    if not found_and_restored:
        print("No modified Steam API DLLs found that needed restoration.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python restore_steam_dlls.py <app_id>")
        sys.exit(1)

    app_id = sys.argv[1]
    if not app_id.isdigit():
        print("Error: App ID must be numeric.")
        sys.exit(1)

    print("--- Steam DLL Restorer ---")
    steam_path = find_steam_install_path()
    if not os.path.isdir(steam_path):
        print(f"Error: Could not find Steam installation directory at {steam_path}")
        sys.exit(1)
    print(f"Found Steam installation at: {steam_path}")

    libraries = find_steam_library_folders(steam_path)
    print(f"Found {len(libraries)} Steam library folder(s).")

    game_path = find_game_install_path(libraries, app_id)
    if not game_path:
        print(f"\nError: Could not find installation directory for App ID: {app_id}")
        print("Please ensure the game is installed.")
        sys.exit(1)
    
    restore_dlls(game_path, steam_path)

if __name__ == "__main__":
    main()
