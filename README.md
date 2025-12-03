# SLS-AH (SLSsteam Achievement Helper)

A power-user's toolkit for Steam on Linux/Steamdeck, providing achievement schema generation and powerful integration with the `SLSsteam` client.

This tool helps you unlock achievements in games that do not have proper schema files and manage your `SLSsteam` configuration for an enhanced experience.

---

## Core Features

*   **Achievement Schema Generation:**
    *   Generate `UserGameStatsSchema` files for games by fetching data directly from the Steam Web API.
    *   Interactive UI to select games from your library or enter App IDs manually.
    *   Smart file handling with options to overwrite, update, or skip existing files.
*   **SLSsteam Config Manager:**
    *   A full menu dedicated to managing your `SLSsteam` configuration (`~/.config/SLSsteam/config.yaml`).
    *   Easily add or remove games from your `AdditionalApps` list.
    *   Enable online multiplayer for certain games with an "Online Fix" feature.
    *   Backup and restore your `SLSsteam` configuration.

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

If you used the installer, you can launch the tool by double-clicking the "SLS-AH" icon on your desktop.

The main menu in the terminal provides access to all the features.

### Main Menu Options

*   **Generate Schema:** The core tool to generate achievement schemas for your games.
*   **Manage SLSsteam App List:** Opens the powerful SLSsteam Config Manager to let you modify your `SLSsteam` setup.
*   **Update / Uninstall:** Manage your installation of this tool.

---

## Detailed Features

### SLSsteam Config Manager

This is a powerful tool to manage your `SLSsteam` configuration file. You can access it from the main menu.

#### Add/Remove Games

You can easily add games to the `AdditionalApps` section of your `SLSsteam` config. This is useful for games that are not automatically detected by `SLSsteam`, such as DLCs or non-Steam games added to your library. When you add a game, you will also be prompted to generate an achievement schema for it immediately.

#### Online Multiplayer Fix

This feature allows you to enable online multiplayer for certain games that would not otherwise work.

*   **How it works:** It adds an entry to the `FakeAppIds` section of your `SLSsteam` config, which routes the game's network traffic through Spacewar (AppID 480). To play with a friend, both of you must be routing through Spacewar.
*   **Disclaimer:** This method is not guaranteed to work for all games. It is known to work for many titles but may not work for games that have more complex networking requirements.

---

## Configuration

On the first run, the script will prompt you for your **Steam Web API Key** and your **Steam User ID**. These are required for fetching achievement data. Please refer to the in-tool instructions for help finding them.

---

## Credits and License

This tool was developed with the assistance of Google's Gemini AI. It is a heavily modified version of the original `generate_emu_config_old` tool from the [gbe_fork_tools](https://github.com/Detanup01/gbe_fork_tools) repository by [Detanup01](https://github.com/Detanup01).

This tool also integrates with [SLSsteam](https://github.com/AceSLS/SLSsteam) by [AceSLS](https://github.com/AceSLS).

This project is licensed under the **GNU Lesser General Public License v3.0**.
