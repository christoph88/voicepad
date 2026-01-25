# VoicePad Test Suite

Test each layer independently before integration. Run these **in order** on your Steam Deck (inside Distrobox Ubuntu).

## Entering Distrobox

Since SteamOS is read-only, you'll run everything inside a Distrobox container.

**First time setup:**
```bash
# Create Ubuntu container with input device access (if not already created)
distrobox create --name ubuntu --image ubuntu:latest --additional-flags "--device=/dev/input"
```

**Enter the container:**
```bash
distrobox enter ubuntu
```

All commands in this guide should be run inside the Distrobox container.

**Important:** The `--device=/dev/input` flag gives the container access to input devices, which is required for PTT detection and button injection.

## Prerequisites

```bash
# Install dependencies (inside Distrobox)
sudo apt update
sudo apt install -y python3-pip python3-pyaudio evtest python3-evdev

# Install Python packages (use --break-system-packages since we're in a container)
pip3 install --break-system-packages sounddevice numpy vosk

# Install python-uinput (requires system dependencies first)
sudo apt install -y libudev-dev python3-setuptools build-essential
pip3 install --break-system-packages python-uinput
```

**Note:** Using `--break-system-packages` is safe here since Distrobox containers are isolated from SteamOS.

### Download Vosk Model

```bash
cd ~/voicepad
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip
```

---

## Test 1: Microphone Capture

**Verifies:** Your mic is detected and capturing audio.

```bash
python3 ~/voicepad/tests/01_mic_level.py
```

**✅ PASS:** RMS numbers change when you talk  
**❌ FAIL:** Error or RMS stays ~0.0000 → mic device issue

---

## Test 2: Vosk Recognition

**Verifies:** Vosk loads and recognizes your voice.

**Before running:** Update `MODEL_PATH` in [02_vosk_print.py](02_vosk_print.py) if needed.

```bash
python3 ~/voicepad/tests/02_vosk_print.py
```

**Note:** This test auto-detects your mic's sample rate (likely 48kHz on Steam Deck) and resamples to 16kHz for Vosk.

**✅ PASS:** Saying "mag" prints partial and final text  
**❌ FAIL:** Mishears you → add aliases to `PHRASES`

---

## Test 3: Push-to-Talk Detection

**Verifies:** PTT button/paddle is readable.

### Step 3A: Configure Steam Input (Important!)

**Before running evtest**, you need to map your back paddle to a keyboard key:

1. Open Steam (Desktop Mode)
2. Settings → Controller → Desktop Configuration
3. Select your back paddle
4. Choose **Keyboard**
5. Select **F13**, **F14**, **F15** (or F12 if those aren't available)
6. Apply and save

**Why:** Steam Input intercepts controller buttons. Mapping to a keyboard key makes it visible to evdev.

### Step 3B: Find your PTT device

**Important:** Due to permission restrictions, run evtest on the **host SteamOS** (not inside Distrobox):

```bash
# Exit Distrobox first
exit

# Run on SteamOS host
sudo evtest
```
Verify you see proper key events

When you press your paddle, you should see:
```
Event: time ..., type 1 (EV_KEY), code 88 (KEY_F12), value 1
Event: time ..., type 1 (EV_KEY), code 88 (KEY_F12), value 0
```

**✅ PASS:** Clean KEY_F12 events  
**❌ FAIL:** Escape sequences like `^[[24~` → Steam Input still processing it, try different key

### Step 3D: Update and run test

Edit [03_ptt_read.py](03_ptt_read.py) with your device/key (likely `/dev/input/event6` and `KEY_F12`).

**Note:** The Python scripts will work from inside Distrobox with the `--device=/dev/input` flag, even though evtest doesn't. Run test 03:

```bash
# Re-enter Distrobox
distrobox enter ubuntu

# Run the test
python3 ~/voicepad/tests/03_ptt_read.py
```

**✅ PASS:** Prints "PTT DOWN" / "PTT UP" immediately  
**❌ FAIL:** Permission error → Python scripts need same host access as evtestev/input flag)
python3 ~/voicepad/tests/03_ptt_read.py
```

**✅ PASS:** Prints "PTT DOWN" / "PTT UP" immediately  
**❌ FAIL:** No output or errors → wrong device/key

---

## Test 4: Button Injection

**Verifies:** uinput can inject gamepad buttons.

### Step 4A: Run injector

```bash
python3 ~/voicepad/tests/04_uinput_tap.py
```

### Step 4B: Verify with evtest

In another terminal:

```bash
sudo evtest
```

Select the new **uinput** device. You should see BTN_X press/release.

**✅ PASS:** evtest shows injected button  
**❌ FAIL:** Permission error or no events → check /dev/uinput permissions

---

## Test 5: PTT + STT Integration (Print Only)

**Verifies:** Full recognition pipeline without injection.

**Before running:** Update `PTT_DEVICE` and `PTT_KEY` in [05_ptt_stt_print.py](05_ptt_stt_print.py) from Test 3.

```bash
python3 ~/voicepad/tests/05_ptt_stt_print.py
```

Hold PTT and say "mag".

**✅ PASS:** Prints "MATCH: mag"  
**❌ FAIL:** No match → revisit Tests 2 and 3

---

## Test 6: Full End-to-End

**Verifies:** Complete pipeline: PTT → STT → button injection.

**Before running:** Update `PTT_DEVICE` and `PTT_KEY` in [06_ptt_stt_inject.py](06_ptt_stt_inject.py).

```bash
python3 ~/voicepad/tests/06_ptt_stt_inject.py
```

Hold PTT and say "reload" or "mag".

**✅ PASS:** Prints "FIRED: reload" and game/evtest sees button  
**❌ FAIL:** Check all previous tests

---

## Troubleshooting

### Mic not working
- Run `arecord -l` to list devices
- Specify device explicitly: `sd.InputStream(device=0, ...)`

### PTT not detected
- **First**: Map paddle to F13/F14/F15 in Steam Input (Desktop Configuration)
- Device should be `/dev/input/event6` (AT Translated Set 2 keyboard)
- If you see escape sequences instead of KEY events, Steam Input is still processing it - try a different F-key
- Test with `sudo evtest` on host first, then in Distrobox

### uinput permission denied
```bash
sudo chmod 666 /dev/uinput
```

Or add your user to the `input` group:
```bash
sudo usermod -a -G input $USER
```

### Vosk not recognizing your accent
- Add phonetic variants to `PHRASES`: `["reload", "real load", "ree load"]`
- Try a larger model
- Use partial results (faster but less accurate)

### Steam Input conflicts
- If PTT doesn't work in-game later, also map the paddle in your **per-game controller configuration**
- Desktop Mode and Gaming Mode have separate controller configs
- Use F13-F15 (avoid F1-F12 which games might use)

---

## Next Steps

After all tests pass, report:
1. Your PTT device path and key code
2. Which phrases Vosk recognized reliably
3. Any issues encountered

Then we'll build the full application with proper configuration and error handling.
