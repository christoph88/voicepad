#!/bin/bash
# Setup InputPlumber for VoicePad PTT
# This script enables InputPlumber to intercept Steam Deck controller for back paddle PTT

set -e

echo "=== VoicePad InputPlumber Setup ==="
echo

# Check if running on Steam Deck
if ! grep -q "Jupiter\|Galileo" /sys/class/dmi/id/product_name 2>/dev/null; then
    echo "⚠ Warning: This doesn't appear to be a Steam Deck"
    echo "Product: $(cat /sys/class/dmi/id/product_name 2>/dev/null || echo 'Unknown')"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Backup Steam's controller config (if exists)
STEAM_CONTROLLER_CONF="/home/deck/.steam/steam/controller_base/empty.vdf"
if [ -f "$STEAM_CONTROLLER_CONF" ]; then
    echo "📦 Backing up Steam controller config..."
    cp "$STEAM_CONTROLLER_CONF" "$STEAM_CONTROLLER_CONF.voicepad.bak"
fi

# Check if InputPlumber is installed
if ! command -v inputplumber &> /dev/null; then
    echo "✗ InputPlumber is not installed"
    echo "Install with: sudo pacman -S inputplumber"
    exit 1
fi

echo "✓ InputPlumber is installed"

# Enable and start InputPlumber service
echo "🚀 Starting InputPlumber service..."
sudo systemctl enable inputplumber
sudo systemctl start inputplumber

# Wait for service to be ready
sleep 2

# Check if service is running
if ! systemctl is-active --quiet inputplumber; then
    echo "✗ Failed to start InputPlumber"
    echo "Check logs: sudo journalctl -u inputplumber -n 50"
    exit 1
fi

echo "✓ InputPlumber service is running"

# Check for Steam Deck composite device
echo
echo "📋 Checking for Steam Deck device..."
DEVICE_INFO=$(inputplumber devices list 2>&1 || echo "ERROR")

if echo "$DEVICE_INFO" | grep -q "Steam Deck"; then
    echo "✓ Steam Deck device detected by InputPlumber"
    DEVICE_ID=0
else
    echo "⚠ Steam Deck device not auto-detected"
    echo
    echo "Device list:"
    echo "$DEVICE_INFO"
    echo
    read -p "Enter composite device ID to use (usually 0): " DEVICE_ID
fi

# Copy VoicePad profile to InputPlumber profiles directory
echo
echo "📄 Installing VoicePad PTT profile..."
PROFILE_SOURCE="$(dirname "$0")/voicepad_ptt.yaml"
PROFILE_DEST="/home/deck/.config/inputplumber/profiles/voicepad_ptt.yaml"

if [ ! -f "$PROFILE_SOURCE" ]; then
    echo "✗ Profile file not found: $PROFILE_SOURCE"
    exit 1
fi

mkdir -p "$(dirname "$PROFILE_DEST")"
cp "$PROFILE_SOURCE" "$PROFILE_DEST"
echo "✓ Profile installed to: $PROFILE_DEST"

# Load the profile
echo
echo "🔧 Loading VoicePad profile..."
inputplumber device "$DEVICE_ID" profile load "$PROFILE_DEST"

# Enable intercept mode to route events to DBus
echo "🎯 Enabling intercept mode (routes events to DBus)..."
inputplumber device "$DEVICE_ID" intercept set pass

echo
echo "=== Setup Complete! ==="
echo
echo "Next steps:"
echo "1. Test PTT detection:"
echo "   python3 ~/voicepad/tests/07_inputplumber_ptt_dbus.py"
echo
echo "2. Press the back paddle R4 (unmapped) to test"
echo
echo "To enable full intercept mode (all buttons to DBus):"
echo "   inputplumber device $DEVICE_ID intercept set all"
echo
echo "To rollback, run: ./rollback_inputplumber.sh"
echo
