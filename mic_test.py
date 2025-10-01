import serial
import matplotlib.pyplot as plt
from collections import deque

# Einstellungen
PORT = "COM3"   # Anpassen!
BAUD = 115200
BURST_SIZE = 512
NUM_BURSTS = 8  # Wieviel in den Plot passen soll (4 Bursts = 4*512 Werte)

# Seriell verbinden
ser = serial.Serial(PORT, BAUD)

# Ringpuffer für alle Samples
signal = deque(maxlen=BURST_SIZE * NUM_BURSTS)

plt.ion()
fig, ax = plt.subplots()

while True:
    line = ser.readline().decode("utf-8").strip()
    try:
        data = [int(x) for x in line.split(",") if x]
        if len(data) == BURST_SIZE:
            # Neue Samples anhängen
            signal.extend(data)

            # Plot aktualisieren
            ax.clear()
            ax.plot(list(signal))
            ax.set_title("Mikrofon Live (hintereinander)")
            ax.set_ylim(0, 40)  # 10-bit ADC Bereich
            ax.set_xlabel("Samples")
            ax.set_ylabel("Amplitude")
            plt.pause(0.01)
    except Exception as e:
        print("Fehler beim Parsen:", e)
