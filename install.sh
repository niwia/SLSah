#!/bin/bash

# Stop on error
set -e

# Installation directory
INSTALL_DIR="$HOME/steam-schema-generator"

# GitHub repository URL (REPLACE WITH YOUR REPO URL)
REPO_URL="https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git"

# Create installation directory
echo "Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone the repository or pull the latest changes
if [ -d ".git" ]; then
    echo "Updating existing installation..."
    git pull
else
    echo "Cloning repository..."
    git clone "$REPO_URL" .
fi

# Create a virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment and install dependencies
echo "Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt
deactivate

# Create the desktop shortcut
DESKTOP_SHORTCUT_PATH="$HOME/Desktop/steam-schema-generator.desktop"
echo "Creating desktop shortcut at $DESKTOP_SHORTCUT_PATH..."

cat > "$DESKTOP_SHORTCUT_PATH" <<EOL
[Desktop Entry]
Name=Steam Schema Generator
Comment=Generate Steam schema files
Exec=konsole -e "bash -c 'cd \"$INSTALL_DIR\" && source .venv/bin/activate && python generate_schema_from_api.py; read -p \"Press Enter to exit\"'"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
EOL

chmod +x "$DESKTOP_SHORTCUT_PATH"

echo "
Installation complete!

You can now run the Steam Schema Generator by double-clicking the icon on your desktop.
"
