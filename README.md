# SLS-AH (SLSsteam Achievement Helper)

A power-user's toolkit for Steam on Linux/Steamdeck, providing achievement schema generation and powerful integration with the `SLSsteam` client.

This tool helps you unlock achievements in games that do not have proper schema files and manage your `SLSsteam` configuration for an enhanced experience.

**Version 2.0** - Now with encrypted credential storage, game search, and enhanced reliability!

---

## Core Features

*   **Achievement Schema Generation:**
    *   Generate `UserGameStatsSchema` files for games by fetching data directly from the Steam Web API.
    *   Interactive UI to select games from your library or enter App IDs manually.
    *   **NEW:** Search for games by name - no need to know the App ID!
    *   Smart file handling with options to overwrite, update, or skip existing files.
    *   **NEW:** Automatic retry logic with exponential backoff for unreliable connections.
*   **Secure Credential Management:**
    *   **NEW:** AES-256-GCM encrypted credential storage (replaces plaintext .env files).
    *   Automatic migration from old .env format.
    *   Machine-specific encryption keys for enhanced security.
*   **SLSsteam Config Manager:**
    *   A full menu dedicated to managing your `SLSsteam` configuration (`~/.config/SLSsteam/config.yaml`).
    *   Easily add or remove games from your `AdditionalApps` list.
    *   Enable online multiplayer for certain games with an "Online Fix" feature.
    *   **NEW:** Comprehensive guide with list of known compatible games.
    *   Backup and restore your `SLSsteam` configuration.

---

## What's New in Version 2.0

**🔐 Enhanced Security:**
*   Credentials are now stored using AES-256-GCM encryption instead of plaintext .env files
*   Automatic migration from old credential format
*   Machine-specific encryption keys

**🔍 Better Usability:**
*   Search for games by name - no need to know App IDs!
*   Improved UI with better visual feedback
*   Version flag: `python slsah.py --version`

**🔧 Improved Reliability:**
*   Automatic retry logic with exponential backoff for API calls
*   Better error handling and recovery
*   Modular codebase for easier maintenance

**📖 Better Documentation:**
*   Comprehensive online fix guide with known compatible games
*   Detailed troubleshooting information

---

## Installation

### Easy Installer (Recommended)

Run the following command in your terminal. This will download the tool, install dependencies, and create a desktop shortcut.

```bash
curl -L https://github.com/niwia/SLSah/raw/main/install.sh | sh
```

### Development Version

To test the latest features from the `dev` branch, run this command. It will be installed in a separate directory (`~/steam-schema-generator-dev`).

```bash
curl -L https://github.com/niwia/SLSah/raw/dev/install_dev.sh | sh
```

---

## Usage

If you used the installer, you can launch the tool by double-clicking the "SLS-AH" icon on your desktop, or run:

```bash
python ~/steam-schema-generator/slsah.py
```

### Command Line Options

```bash
# Show version
python slsah.py --version

# Clear stored credentials
python slsah.py --clear-credentials
```

### First Run

On the first run, the script will prompt you for your **Steam Web API Key** and your **Steam User ID**. These are encrypted and securely stored locally.

### Steam Web API Key

**Important:** You can use an API key from any Steam account. It does not need to be from your primary account. This key is only used to fetch public achievement data and is not linked to your account for any other purpose.

1.  Go to the Steam API Key page: [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
2.  You will be asked for a domain name. This does not matter, you can enter any value (e.g., `localhost`).
3.  Once you agree to the terms, you will be given a key. Copy this key for the script setup.

<img src="thumbnails/webapi.png" alt="Steam Web API Key" width="500"/>

### Steam User ID

It is important to use your own Steam User ID. This ID is used to name the generated stats file (e.g., `UserGameStats_{YourID}_{AppID}.bin`), which allows the Steam client to correctly associate the achievement data with your profile.

**Important:** Some tools or websites might give you an ID in the format `[U:1:11223344]`. The script is smart enough to handle this, but the number you need is the last part, e.g., `11223344`.

There are several ways to find your ID. The easiest is through the Steam client:

1.  In the Steam client, open your "Friends & Chat" window.

    <img src="thumbnails/friends1.png" alt="Friends & Chat" width="300"/>
2.  Click "Add a Friend".

    <img src="thumbnails/friends2.png" alt="Add a Friend" width="500"/>
3.  Your Account ID is displayed at the top. This is the number you need to copy for the script setup.

    <img src="thumbnails/steamaid.png" alt="Steam Account ID" width="500"/>

Alternatively, you can use websites like [SteamDB](https://steamdb.info/) (look for `steam3ID`) or [SteamID.io](https://steamid.io/).

<img src="thumbnails/steamdb.png" alt="SteamDB Profile" width="500"/>
<img src="thumbnails/steamid.png" alt="SteamID.io Profile" width="500"/>

## Installation

### Easy Installer (Recommended)

Run the following command in your terminal. This will download the script, install dependencies, and create a desktop shortcut.

```bash
curl -L https://github.com/niwia/SLSah/raw/main/install.sh | sh
```

### Development Version (for testing)

If you want to test the latest features and bug fixes, you can install the `dev` branch version. This will be installed in a separate directory (`~/steam-schema-generator-dev`) and will not interfere with your main installation.

Run the following command in your terminal:

```bash
curl -L https://github.com/niwia/SLSah/raw/dev/install_dev.sh | sh
```

### Manual Installation

If you prefer to set up the tool manually:

1.  Clone or download this repository.
2.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

*   **Installer:** If you used the installer, simply double-click the "Steam Schema Generator" icon on your desktop to run the tool.
*   **Manual:** If you installed manually, you can run the script directly from your terminal:
    ```bash
    python3 generate_schema_from_api.py
    ```

## Updating

There are two ways to update the tool to the latest version:

1.  **From the Main Menu:** Simply select the "Update" option from the main menu of the tool.
2.  **From the Terminal:** Run the installer command again.

In both cases, the script will automatically fetch the latest files while preserving your settings.

```bash
curl -L https://github.com/niwia/SLSah/raw/main/install.sh | sh
```

## Uninstalling

There are two ways to uninstall the tool:

1.  **From the Main Menu:** Simply select the "Uninstall" option from the main menu of the tool.
2.  **From the Terminal:** Run the `uninstall.sh` script.
    1.  Open a terminal.
    2.  Navigate to the installation directory:
        ```bash
        cd ~/steam-schema-generator
        ```
    3.  Run the uninstaller:
        ```bash
        bash uninstall.sh
        ```

This will remove the application and the desktop shortcut. Your generated schema files in the Steam directory will not be deleted.

## Alternatives

If you prefer a tool that uses your Steam login credentials instead of a Steam Web API key, you can check out [SLScheevo](https://github.com/xamionex/SLScheevo). It is another excellent tool that achieves a similar goal but uses a different authentication method.

## Credits and License

This tool was developed with the assistance of Google's Gemini AI. It is a heavily modified version of the original `generate_emu_config_old` tool from the [gbe_fork_tools](https://github.com/Detanup01/gbe_fork_tools) repository by [Detanup01](https://github.com/Detanup01).

This tool also integrates with [SLSsteam](https://github.com/AceSLS/SLSsteam) by [AceSLS](https://github.com/AceSLS) to provide a more automated workflow.

This project is licensed under the **GNU Lesser General Public License v3.0**, the same license as the original project. You can find a copy of the license in the `LICENSE` file.