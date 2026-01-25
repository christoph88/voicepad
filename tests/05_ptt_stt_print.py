import queue, json, time, threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from evdev import InputDevice, ecodes

MODEL = "/home/deck/voicepad/models/vosk-model-small-en-us-0.15"
PHRASES = ["reload", "mag", "breach", "flash", "stack up", "open"]

PTT_DEVICE = "/dev/input/event4"  # TODO: Update from test 03
PTT_KEY = "KEY_F20"  # TODO: Update from test 03

model = Model(MODEL)
rec = KaldiRecognizer(model, 16000, json.dumps(PHRASES))

q = queue.Queue()
listening = False

def audio_cb(indata, frames, time_info, status):
    if listening:
        q.put(bytes(indata))

def ptt_thread():
    global listening
    dev = InputDevice(PTT_DEVICE)
    code = ecodes.ecodes[PTT_KEY]
    for e in dev.read_loop():
        if e.type == ecodes.EV_KEY and e.code == code:
            listening = (e.value == 1)
            print("PTT", "DOWN" if listening else "UP")

threading.Thread(target=ptt_thread, daemon=True).start()

print("Hold PTT and speak one of:", PHRASES)

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=audio_cb):
    while True:
        if not q.empty():
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "")
                if text:
                    print("MATCH:", text)
