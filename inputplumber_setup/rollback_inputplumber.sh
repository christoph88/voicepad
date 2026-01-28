#!/bin/bash
# Rollback InputPlumber setup and restore original Steam Deck controller behavior

set -e

echo "=== VoicePad InputPlumber Rollback ==="
echo

# Stop InputPlumber service
echo "🛑 Stopping InputPlumber service..."
sudo systemctl stop inputplumber

# Disable InputPlumber from auto-starting
echo "🔧 Disabling InputPlumber auto-start..."
sudo systemctl disable inputplumber

# Restore Steam controller config backup (if exists)
STEAM_CONTROLLER_CONF="/home/deck/.steam/steam/controller_base/empty.vdf"
if [ -f "$STEAM_CONTROLLER_CONF.voicepad.bak" ]; then
    echo "📦 Restoring Steam controller config backup..."
    mv "$STEAM_CONTROLLER_CONF.voicepad.bak" "$STEAM_CONTROLLER_CONF"
fi

# Remove VoicePad profile
PROFILE_DEST="/home/deck/.config/inputplumber/profiles/voicepad_ptt.yaml"
if [ -f "$PROFILE_DEST" ]; then
    echo "🗑️  Removing VoicePad profile..."
    rm "$PROFILE_DEST"
fi

# Remove modified Steam Deck config (restores auto_manage: false)
LOCAL_CONFIG="/home/deck/.config/inputplumber/devices/50-steam_deck.yaml"
if [ -f "$LOCAL_CONFIG" ]; then
    echo "🗑️  Removing modified Steam Deck config..."
    rm "$LOCAL_CONFIG"
    # Remove directory if empty
    rmdir /home/deck/.config/inputplumber/devices 2>/dev/null || true
fi

# Restart Steam to restore normal controller handling
echo "🔄 Restarting Steam to restore controller..."
if pgrep -x "steam" > /dev/null; then
    killall steam 2>/dev/null || true
    sleep 2
    echo "⚠ Steam stopped. Please restart it manually from Gaming Mode."
else
    echo "✓ Steam is not running"
fi

echo
echo "=== Rollback Complete! ==="
echo
echo "Your Steam Deck controller is back to normal Steam Input control."
echo
echo "To verify:"
echo "1. Restart Steam (if not already restarted)"
echo "2. Test controller in a game"
echo "3. Back paddles should work as before"
echo
echo "InputPlumber is still installed but disabled."
echo "To completely remove it: sudo pacman -R inputplumber"
echo
