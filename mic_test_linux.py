import serial
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

PORT = ("/dev/ttyUSB0")     # anpassen
BAUD = 921600
BURST_SIZE = 512
NUM_BURSTS = 4

ser = serial.Serial(PORT, BAUD, timeout=0.1)
signal = deque(maxlen=BURST_SIZE * NUM_BURSTS)
buf = ""

plt.ion()
fig, ax = plt.subplots()
paused = False  # Status-Flag

def on_key(event):
    global paused
    if event.key == " ":
        paused = not paused
        print("Pause =", paused)

fig.canvas.mpl_connect("key_press_event", on_key)

while True:
    if not paused:
        data = ser.read(ser.in_waiting or 64)
        if data:
            buf += data.decode("utf-8", errors="ignore")

            while "<START>" in buf and "<END>" in buf:
                s = buf.find("<START>") + len("<START>")
                e = buf.find("<END>")
                burst_str = buf[s:e]
                buf = buf[e + len("<END>"):]
                try:
                    arr = np.fromstring(burst_str, dtype=int, sep=",")
                    if arr.size == BURST_SIZE:
                        signal.extend(arr.tolist())
                        x = np.arange(len(signal)) / 1000.0  # 1 kHz → Sekunden
                        ax.clear()
                        ax.plot(x, list(signal))
                        ax.set_ylim(0, 1023)
                        ax.set_xlabel("Zeit (s)")
                        ax.set_ylabel("ADC")
                        ax.set_title("ESP32 Mikrofon Live  (Leertaste = Pause)")
                        plt.pause(0.001)
                except Exception as ex:
                    print("Parsing-Fehler:", ex)
    else:
        # Wenn pausiert: nur die GUI am Leben halten (Zoom etc.)
        plt.pause(0.05)
