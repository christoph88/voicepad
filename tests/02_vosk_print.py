import queue, json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = "/home/deck/voicepad/models/vosk-model-small-en-us-0.15"
PHRASES = ["reload", "mag", "breach", "flash", "stack up", "open"]

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000, json.dumps(PHRASES))

q = queue.Queue()
def cb(indata, frames, time_info, status):
    q.put(bytes(indata))

print("Say one of:", PHRASES)
print("Ctrl+C to stop\n")

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=cb):
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            print("FINAL  ", json.loads(rec.Result()))
        else:
            pres = json.loads(rec.PartialResult())
            if pres.get("partial"):
                print("PARTIAL", pres)
