# VoicePad Test Suite

Test each layer independently before integration. Run these **in order** on your Steam Deck (inside Distrobox Ubuntu).

## Prerequisites

```bash
# Install dependencies (inside Distrobox)
sudo apt update
sudo apt install -y python3-pip python3-pyaudio evtest
pip3 install sounddevice numpy vosk python-evdev python-uinput
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

**✅ PASS:** Saying "mag" prints partial and final text  
**❌ FAIL:** Mishears you → add aliases to `PHRASES`

---

## Test 3: Push-to-Talk Detection

**Verifies:** PTT button/paddle is readable.

### Step 3A: Find your PTT device

```bash
sudo evtest
```

Press your PTT button and note:
- Device path (e.g., `/dev/input/event4`)
- Key name (e.g., `KEY_F20`)

### Step 3B: Update and run test

Edit [03_ptt_read.py](03_ptt_read.py) with your device/key, then:

```bash
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
- Try all `/dev/input/event*` devices in evtest
- Check Steam Input isn't intercepting the button

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

---

## Next Steps

After all tests pass, report:
1. Your PTT device path and key code
2. Which phrases Vosk recognized reliably
3. Any issues encountered

Then we'll build the full application with proper configuration and error handling.
