#!/bin/bash
# Diagnostic script to debug InputPlumber Steam Deck detection

echo "=== InputPlumber Steam Deck Diagnostics ==="
echo

echo "1. System Information:"
echo "  Product: $(cat /sys/class/dmi/id/product_name)"
echo "  Vendor: $(cat /sys/class/dmi/id/sys_vendor)"
echo

echo "2. Looking for Steam Deck controller (hidraw):"
echo "  Expected: VID=0x28de, PID=0x1205"
echo
ls -la /dev/hidraw* 2>/dev/null || echo "  No hidraw devices found"
echo

echo "3. Checking hidraw device details:"
for device in /dev/hidraw*; do
    if [ -e "$device" ]; then
        echo "  Device: $device"
        sudo cat "/sys/class/hidraw/$(basename $device)/device/uevent" 2>/dev/null | grep -E "HID_NAME|HID_ID" || true
        echo
    fi
done

echo "4. Checking evdev devices:"
ls -la /dev/input/event* | head -10
echo

echo "5. InputPlumber service status:"
systemctl status inputplumber --no-pager | head -20
echo

echo "6. InputPlumber recent logs:"
sudo journalctl -u inputplumber -n 30 --no-pager
echo

echo "7. Checking if Steam is running:"
if pgrep -x "steam" > /dev/null; then
    echo "  ⚠ Steam is running (may be holding device)"
    echo "  Try stopping Steam: killall steam"
else
    echo "  ✓ Steam is not running"
fi
echo

echo "8. InputPlumber config check:"
if [ -f "/home/deck/.config/inputplumber/devices/50-steam_deck.yaml" ]; then
    echo "  ✓ Local config exists"
    grep "auto_manage" /home/deck/.config/inputplumber/devices/50-steam_deck.yaml
else
    echo "  ✗ Local config not found"
fi
echo

echo "9. Checking source devices from config:"
echo "  Looking for hidraw with VID=28de PID=1205..."
for hidraw in /sys/class/hidraw/hidraw*/device; do
    if [ -d "$hidraw" ]; then
        VID=$(cat "$hidraw/id/vendor" 2>/dev/null)
        PID=$(cat "$hidraw/id/product" 2>/dev/null)
        if [ "$VID" = "0x28de" ] || [ "$VID" = "28de" ]; then
            echo "  ✓ Found Valve device: $hidraw"
            echo "    VID: $VID, PID: $PID"
        fi
    fi
done
