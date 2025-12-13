#!/bin/bash

# Stop on error
set -e

# Installation directory
INSTALL_DIR="$HOME/steam-schema-generator"

# GitHub repository URL (REPLACE WITH YOUR REPO URL)
REPO_URL="https://github.com/niwia/SLSah.git"

# Create installation directory
echo "Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone the repository or pull the latest changes
if [ -d ".git" ]; then
    echo "Updating existing installation..."
    echo "Discarding any local changes..."
    git reset --hard HEAD
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

# Make the run script executable
chmod +x run.sh

# Create the desktop shortcut
DESKTOP_SHORTCUT_PATH="$HOME/Desktop/SLS-AH.desktop"
echo "Creating desktop shortcut at $DESKTOP_SHORTCUT_PATH..."

cat > "$DESKTOP_SHORTCUT_PATH" <<EOL
[Desktop Entry]
Name=SLS-AH
Comment=SLSsteam Achievement Helper v2.0
Exec=konsole -e "$INSTALL_DIR/run.sh"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
EOL

chmod +x "$DESKTOP_SHORTCUT_PATH"


echo "
Installation complete!

You can now run SLS-AH by:
- Double-clicking the 'SLS-AH' icon on your desktop
- Or running: cd $INSTALL_DIR && ./run.sh
"
