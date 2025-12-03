# SLS-AH (SLSsteam Achievement Helper)

A tool to generate `UserGameStatsSchema` and `UserGameStats` files for Steam games using the Steam Web API, designed for Linux/Steamdeck and the `SLSsteam` client.

This tool helps you unlock achievements in games that do not have proper schema files, by fetching the necessary achievement data directly from Steam.

---

## Features

*   **Interactive UI:** A simple and easy-to-use terminal interface for a smooth workflow.
*   **Multiple Game Sources:**
    *   Scan your `SLSsteam` config file.
    *   Scan your main Steam library.
    *   Enter a Steam App ID manually.
*   **API Key & User ID Management:** Securely saves your Steam Web API key and User ID in a local `.env` file so you only have to enter them once.
*   **Smart File Handling:** Intelligently handles existing schema files with options to:
    *   **Overwrite:** Replace the existing file completely.
    *   **Update:** Merge new achievements into the existing file.
    *   **Skip:** Do nothing if a file already exists.
*   **Game Name Display:** Shows the name of the game being processed for clarity.
*   **Summary Report:** Provides a summary of all operations performed at the end of the process.

---

## Configuration

On the first run, the script will prompt you for your **Steam Web API Key** and your **Steam User ID**.

### Steam Web API Key
You can get a key from any Steam account; it does not need to be from your primary account.

1.  Go to the Steam API Key page: [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
2.  Enter any domain name (e.g., `localhost`) and agree to the terms.
3.  Copy the generated key.

<img src="thumbnails/webapi.png" alt="Steam Web API Key" width="500"/>

### Steam User ID
It's important to use your own Steam User ID so the generated files are correctly associated with your profile.

The easiest way to find your ID is in the Steam client:
1.  Open the "Friends & Chat" window.
2.  Click "Add a Friend".
3.  Your Account ID is displayed at the top.

<img src="thumbnails/steamaid.png" alt="Steam Account ID" width="500"/>

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

*   **Desktop Shortcut:** If you used the installer, double-click the "SLS-AH" icon on your desktop.
*   **Manual:** To run the script manually from your terminal:
    ```bash
    python3 generate_schema_from_api.py
    ```

---

## Updating & Uninstalling

You can **update** or **uninstall** the tool directly from its main menu.

Alternatively, you can re-run the installer command to update, or run the `uninstall.sh` script in the installation directory (`~/steam-schema-generator`) to uninstall.

---

## Credits and License

This tool was developed with the assistance of Google's Gemini AI. It is a heavily modified version of the original `generate_emu_config_old` tool from the [gbe_fork_tools](https://github.com/Detanup01/gbe_fork_tools) repository by [Detanup01](https://github.com/Detanup01).

This tool also integrates with [SLSsteam](https://github.com/AceSLS/SLSsteam) by [AceSLS](https://github.com/AceSLS).

This project is licensed under the **GNU Lesser General Public License v3.0**.