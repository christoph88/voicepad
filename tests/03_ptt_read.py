from evdev import InputDevice, ecodes

DEVICE = "/dev/input/event6"  # Keyboard device
KEY = "KEY_INSERT"  # Update with your mapped key
dev = InputDevice(DEVICE)
code = ecodes.ecodes[KEY]

print("Listening for PTT... press/release your button\n")

for e in dev.read_loop():
    if e.type == ecodes.EV_KEY and e.code == code:
        if e.value == 1:
            print("PTT DOWN")
        elif e.value == 0:
            print("PTT UP")
