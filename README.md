# Steam Schema Generator

This tool allows you to generate `UserGameStatsSchema` and `UserGameStats` files for Steam games using the Steam Web API.

## Features

*   **Interactive UI:** A simple and easy-to-use terminal interface.
*   **API Key & User ID Management:** Securely saves your Steam API key and User ID so you only have to enter them once.
*   **SLSsteam Integration:** Automatically generate files for all games in your SLSsteam `config.yaml`.
*   **Smart File Handling:** Intelligently handles existing files with options to overwrite, update (merge new achievements), or skip.
*   **Game Name Display:** Shows the name of the game being processed.
*   **Summary Report:** Provides a summary of the operations performed.

## Installation

Run the following command in your terminal:

```bash
curl -L https://github.com/niwia/SLSah/raw/main/install.sh | sh
```

This will download and run the installer, which will create a shortcut on your desktop.

## Usage

Double-click the "Steam Schema Generator" icon on your desktop to run the tool.

## Credits and License

This tool was developed with the assistance of Google's Gemini AI. It is a heavily modified version of the original `generate_emu_config_old` tool from the [gbe_fork_tools](https://github.com/Detanup01/gbe_fork_tools) repository by [Detanup01](https://github.com/Detanup01).

This tool also integrates with [SLSsteam](https://github.com/AceSLS/SLSsteam) by [AceSLS](https://github.com/AceSLS) to provide a more automated workflow.

This project is licensed under the **GNU Lesser General Public License v3.0**, the same license as the original project. You can find a copy of the license in the `LICENSE` file.
