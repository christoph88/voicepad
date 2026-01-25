import queue, json, time, threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from evdev import InputDevice, ecodes
import uinput

MODEL = "/home/deck/voicepad/models/vosk-model-small-en-us-0.15"
PHRASES = ["reload", "mag"]

PTT_DEVICE = "/dev/input/event4"  # TODO: Update from test 03
PTT_KEY = "KEY_F20"  # TODO: Update from test 03

model = Model(MODEL)
rec = KaldiRecognizer(model, 16000, json.dumps(PHRASES))

q = queue.Queue()
listening = False

# virtual button to inject (X = "reload" in many layouts)
vpad = uinput.Device([uinput.BTN_X])

def tap_x():
    vpad.emit(ecodes.BTN_X, 1)
    time.sleep(0.08)
    vpad.emit(ecodes.BTN_X, 0)

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

print("Hold PTT and say 'reload' or 'mag' -> inject BTN_X")

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=audio_cb):
    while True:
        if not q.empty():
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "")
                if text in ("reload", "mag"):
                    print("FIRED:", text)
                    tap_x()
