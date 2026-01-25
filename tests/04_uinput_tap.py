import time
import uinput
from evdev import ecodes

device = uinput.Device([uinput.BTN_X])

print("Creating virtual device, tapping BTN_X in 2 seconds...")
time.sleep(2)

device.emit(ecodes.BTN_X, 1)
time.sleep(0.08)
device.emit(ecodes.BTN_X, 0)

print("Done.")
time.sleep(1)
