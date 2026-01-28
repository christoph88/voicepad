# VoicePad InputPlumber Setup - README

## Overview
This directory contains files to configure InputPlumber for back paddle PTT detection on Steam Deck.

## Files
- `voicepad_ptt.yaml` - InputPlumber profile configuration
- `setup_inputplumber.sh` - Setup script (enables InputPlumber, loads profile)
- `rollback_inputplumber.sh` - Rollback script (restores original behavior)

## Installation (Run on Steam Deck)

### 1. Copy files to Steam Deck
```bash
# From your development machine
scp -r inputplumber_setup deck@steamdeck:~/voicepad/
scp tests/07_inputplumber_ptt_dbus.py deck@steamdeck:~/voicepad/tests/
```

### 2. Run setup script
```bash
# On Steam Deck
cd ~/voicepad/inputplumber_setup
./setup_inputplumber.sh
```

The script will:
- ✓ Backup Steam controller config
- ✓ Enable and start InputPlumber service
- ✓ Load VoicePad PTT profile
- ✓ Configure intercept mode

### 3. Test PTT detection
```bash
python3 ~/voicepad/tests/07_inputplumber_ptt_dbus.py
# Press back paddle R4 (unmapped)
```

## Rollback (If something goes wrong)

```bash
cd ~/voicepad/inputplumber_setup
./rollback_inputplumber.sh
```

This will:
- ✓ Stop and disable InputPlumber
- ✓ Restore Steam controller config backup
- ✓ Remove VoicePad profile
- ✓ Restore normal Steam Input behavior

## How It Works

### InputPlumber Architecture
```
Back Paddle R4 → InputPlumber (grabs device) → DBus Event → Python Script (PTT)
                                              ↓
                               Other buttons → Virtual Gamepad → Game
```

**Benefits:**
1. ✅ Back paddle R4 works for PTT (via DBus)
2. ✅ All other buttons pass through to games normally
3. ✅ No external hardware needed
4. ✅ Ergonomic - fingers already on paddles
5. ✅ Full rollback if issues occur

### Intercept Modes
- `none` (0) - Normal passthrough, no interception
- `pass` (1) - Passthrough except Guide button triggers intercept
- `all` (2) - All events routed to DBus (for testing/overlay)
- `gamepad_only` (3) - Only gamepad events to DBus

We use `pass` mode by default for minimal interference.

## Troubleshooting

### InputPlumber not starting
```bash
# Check status
sudo systemctl status inputplumber

# View logs
sudo journalctl -u inputplumber -n 50

# Try manual start
sudo LOG_LEVEL=debug inputplumber
```

### Device not detected
```bash
# List devices
inputplumber devices list

# Check Steam Deck detection
cat /sys/class/dmi/id/product_name
# Should show: Jupiter or Galileo
```

### No DBus events
```bash
# Check intercept mode
inputplumber device 0 intercept get

# Enable full intercept (for testing)
inputplumber device 0 intercept set all

# Test with InputPlumber's built-in tool
inputplumber device 0 test
```

### Controller stops working in games
This means InputPlumber is intercepting too much. Run rollback:
```bash
./rollback_inputplumber.sh
```

### Steam Input conflicts
If Steam is fighting InputPlumber:
1. Rollback InputPlumber
2. In Steam: Settings → Controller → Desktop Configuration
3. Disable controller support temporarily
4. Re-run setup

## Safety Notes

- ⚠ **Backup before setup**: Setup script automatically backs up Steam config
- ⚠ **Test in Desktop Mode first**: Don't test in Gaming Mode initially
- ⚠ **Rollback ready**: Keep terminal access open during testing
- ✓ **Non-destructive**: Rollback restores everything to original state

## Next Steps After Successful Testing

1. Integrate DBus listener into main voicepad.py
2. Combine with Vosk STT (Test 2)
3. Add button injection (Test 4)
4. Build complete voice command pipeline
