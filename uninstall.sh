#!/bin/bash

# Installation directory
INSTALL_DIR="$HOME/steam-schema-generator"
DESKTOP_SHORTCUT_PATH="$HOME/Desktop/steam-schema-generator.desktop"
STATS_DIR="$HOME/.steam/steam/appcache/stats"

echo "This script will remove the Steam Schema Generator and its files."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Remove desktop shortcut
if [ -f "$DESKTOP_SHORTCUT_PATH" ]; then
    echo "Removing desktop shortcut..."
    rm "$DESKTOP_SHORTCUT_PATH"
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing installation directory..."
    rm -rf "$INSTALL_DIR"
fi

echo ""
echo "The application has been uninstalled."
echo ""
echo "The generated schema and stats files are located in:"
echo "$STATS_DIR"
echo "These files have not been deleted. You can remove them manually if you wish."

echo "Uninstallation complete."
