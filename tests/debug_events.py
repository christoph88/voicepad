from evdev import InputDevice

DEVICE = "/dev/input/event6"

dev = InputDevice(DEVICE)
print(f"Reading ALL events from {DEVICE}...")
print("Press your paddle button to see events\n")

for e in dev.read_loop():
    print(e)
