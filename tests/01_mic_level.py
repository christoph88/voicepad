import sounddevice as sd
import numpy as np
import time

print("Listing input devices:\n")
print(sd.query_devices())
print("\nRecording mic level for 10 seconds...\n")

def callback(indata, frames, time_info, status):
    rms = np.sqrt(np.mean(indata.astype(np.float32)**2))
    print(f"RMS: {rms:.4f}")

with sd.InputStream(channels=1, callback=callback):
    time.sleep(10)
