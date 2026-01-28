#!/bin/bash
# Run this on the Steam Deck to check InputPlumber availability

echo "=== Checking InputPlumber Installation ==="
echo

echo "1. Systemd service status:"
systemctl status inputplumber 2>&1 | head -5
echo

echo "2. DBus service check:"
dbus-send --system --print-reply --dest=org.freedesktop.DBus \
  /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null | grep -i shadowblip || echo "Not found via DBus"
echo

echo "3. Package manager check (pacman):"
pacman -Q inputplumber 2>&1 || echo "Not installed via pacman"
echo

echo "4. Flatpak check:"
flatpak list | grep -i input || echo "No input-related flatpaks found"
echo

echo "5. Binary check:"
which inputplumber || echo "Binary not in PATH"
echo

echo "6. CLI test (if installed):"
if which inputplumber >/dev/null 2>&1; then
    inputplumber sources list 2>&1 | head -3 || echo "Daemon not running or CLI failed"
else
    echo "Command not available"
fi
echo

echo "=== Recommendation ==="
if systemctl is-active --quiet inputplumber 2>/dev/null; then
    echo "✓ InputPlumber is INSTALLED and RUNNING - use DBus approach"
else
    echo "✗ InputPlumber NOT installed - use direct evdev approach (simpler)"
fi
