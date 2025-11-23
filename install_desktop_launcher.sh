#!/bin/bash
#
# install_desktop_launcher.sh
# Installs WeighIt desktop launcher for the current user
#

set -e

# Get the absolute path where this script is located (the weighit directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=================================================="
echo "WeighIt Desktop Launcher Installation"
echo "=================================================="
echo ""
echo "Installing from: $SCRIPT_DIR"
echo ""

# Create desktop file from template
echo "📝 Creating desktop launcher..."
sed "s|INSTALL_DIR|${SCRIPT_DIR}|g" weighit.desktop.template > weighit.desktop

# Make launch script executable
echo "🔧 Making launch script executable..."
chmod +x launch.sh

# Install for current user
echo "📦 Installing launcher..."
mkdir -p ~/.local/share/applications
cp weighit.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/weighit.desktop

# Update desktop database (if available)
if command -v update-desktop-database &> /dev/null; then
    echo "🔄 Updating desktop database..."
    update-desktop-database ~/.local/share/applications/
fi

echo ""
echo "✅ Desktop launcher installed successfully!"
echo ""
echo "You can now:"
echo "  • Find 'WeighIt' in your application menu"
echo "  • Pin it to your favorites/taskbar"
echo "  • Create a desktop shortcut"
echo ""
echo "To uninstall, run: rm ~/.local/share/applications/weighit.desktop"
echo "=================================================="
