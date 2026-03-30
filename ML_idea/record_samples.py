import sounddevice as sd
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
import librosa
import librosa.display
import os
import queue
import sys

# =========================
# ⚙️ CONFIG
# =========================
SAMPLE_RATE = 48000
CHANNELS = 1

THRESHOLD = 0.08
MAX_DURATION = 0.3

PRE_BUFFER = 0.02

OUTPUT_DIRS = {
    "h": "samples_hit",
    "m": "samples_miss"
}

# =========================
# 📁 Ordner erstellen
# =========================
for d in OUTPUT_DIRS.values():
    os.makedirs(d, exist_ok=True)

# =========================
# 🔊 Queue
# =========================
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())


# =========================
# 📊 Plot Funktion
# =========================
def plot_sample(audio, sr):
    audio = np.array(audio)

    fig, axs = plt.subplots(2, 1, figsize=(10, 6))

    # 🎵 Waveform
    axs[0].plot(audio)
    axs[0].set_title("Waveform")
    axs[0].set_ylim(-1, 1)

    # 🎼 Spectrogram
    S = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=64)
    S_dB = librosa.power_to_db(S, ref=np.max)

    img = librosa.display.specshow(
        S_dB,
        sr=sr,
        x_axis='time',
        y_axis='mel',
        ax=axs[1]
    )
    axs[1].set_title("Mel Spectrogram")
    fig.colorbar(img, ax=axs[1], format="%+2.0f dB")

    plt.tight_layout()
    plt.show()


# =========================
# 🎤 Aufnahme
# =========================
def record_loop():
    print("🎤 Aufnahme läuft... (Strg+C zum Beenden)")

    pre_buffer = []
    pre_buffer_size = int(PRE_BUFFER * SAMPLE_RATE)

    recording = False
    recorded_audio = []

    sample_counter = 0

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        blocksize=1024
    ):
        while True:
            data = audio_queue.get().flatten()

            # Pre-buffer füllen
            pre_buffer.extend(data)
            if len(pre_buffer) > pre_buffer_size:
                pre_buffer = pre_buffer[-pre_buffer_size:]

            rms = np.sqrt(np.mean(data**2))

            if not recording:
                if rms > THRESHOLD:
                    print("\n🎯 Trigger erkannt!")
                    recording = True
                    recorded_audio = pre_buffer.copy()

            else:
                recorded_audio.extend(data)

                if len(recorded_audio) > SAMPLE_RATE * MAX_DURATION:
                    recording = False

                    audio_np = np.array(recorded_audio)

                    # 📊 Plot anzeigen
                    plot_sample(audio_np, SAMPLE_RATE)

                    # ⌨️ Label wählen
                    key = input(
                        "Speichern? [h=hit / m=miss / d=discard]: "
                    ).strip().lower()

                    if key in OUTPUT_DIRS:
                        folder = OUTPUT_DIRS[key]
                        sample_counter += 1
                        filename = os.path.join(
                            folder,
                            f"sample_{sample_counter:03d}.wav"
                        )
                        sf.write(filename, audio_np, SAMPLE_RATE)
                        print(f"💾 Gespeichert: {filename}")
                    else:
                        print("❌ Verworfen")

                    print("\n🎤 Weiter...")

                    recorded_audio = []


# =========================
# ▶️ MAIN
# =========================
if __name__ == "__main__":
    try:
        record_loop()
    except KeyboardInterrupt:
        print("\n👋 Beendet")