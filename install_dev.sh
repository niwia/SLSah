#!/bin/bash

# Stop on error
set -e

# Installation directory for the dev version
INSTALL_DIR="$HOME/steam-schema-generator-dev"

# GitHub repository URL
REPO_URL="https://github.com/niwia/SLSah.git"

# Create installation directory
echo "Creating dev installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone the dev branch or pull the latest changes
if [ -d ".git" ]; then
    echo "Updating existing dev installation..."
    echo "Discarding any local changes..."
    git reset --hard HEAD
    git checkout dev # Make sure we are on the dev branch
    git pull
else
    echo "Cloning dev branch of the repository..."
    git clone -b dev "$REPO_URL" .
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

# Make the run script executable
chmod +x run.sh

# Create the desktop shortcut for the dev version
DESKTOP_SHORTCUT_PATH="$HOME/Desktop/steam-schema-generator-dev.desktop"
echo "Creating dev desktop shortcut at $DESKTOP_SHORTCUT_PATH..."

cat > "$DESKTOP_SHORTCUT_PATH" <<EOL
[Desktop Entry]
Name=Steam Schema Generator (Dev)
Comment=Generate Steam schema files (Development Version)
Exec=konsole -e "$INSTALL_DIR/run.sh"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
EOL

chmod +x "$DESKTOP_SHORTCUT_PATH"

echo "
Dev installation complete!

You can now run the Steam Schema Generator (Dev) by double-clicking the icon on your desktop.
"
