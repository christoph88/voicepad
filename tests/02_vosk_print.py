import queue, json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import numpy as np

MODEL_PATH = "/home/deck/voicepad/models/vosk-model-small-en-us-0.15"
PHRASES = ["reload", "mag", "breach", "flash", "stack up", "open"]

# Try common sample rates
VOSK_RATE = 16000
for test_rate in [16000, 44100, 48000]:
    try:
        test = sd.InputStream(samplerate=test_rate, channels=1)
        test.close()
        MIC_RATE = test_rate
        print(f"Using mic sample rate: {MIC_RATE} Hz")
        break
    except:
        continue

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, VOSK_RATE, json.dumps(PHRASES))

q = queue.Queue()

def resample(data, from_rate, to_rate):
    """Simple linear resampling"""
    if from_rate == to_rate:
        return data
    ratio = to_rate / from_rate
    new_length = int(len(data) * ratio)
    return np.interp(
        np.linspace(0, len(data) - 1, new_length),
        np.arange(len(data)),
        data
    ).astype(np.int16)

def cb(indata, frames, time_info, status):
    audio = indata.flatten()
    if MIC_RATE != VOSK_RATE:
        audio = resample(audio, MIC_RATE, VOSK_RATE)
    q.put(audio.tobytes())

print("Say one of:", PHRASES)
print("Ctrl+C to stop\n")

with sd.InputStream(samplerate=MIC_RATE, dtype="int16", channels=1, callback=cb):
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            print("FINAL  ", json.loads(rec.Result()))
        else:
            pres = json.loads(rec.PartialResult())
            if pres.get("partial"):
                print("PARTIAL", pres)
