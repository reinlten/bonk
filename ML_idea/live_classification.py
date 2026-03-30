import pygame
import sounddevice as sd
import numpy as np
import librosa
import queue
import sys
import joblib
# =========================
# ⚙️ CONFIG
# =========================
SAMPLE_RATE = 48000
CHANNELS = 1

THRESHOLD = 0.08
MAX_DURATION = 0.3
PRE_BUFFER = 0.02

CONFIDENCE_THRESHOLD = 0.75
COOLDOWN = 2  # Sekunden

pygame.mixer.init(frequency=SAMPLE_RATE)

hit_sound = pygame.mixer.Sound("Sounds\\hit\\lets-go-meme.mp3")
miss_sound = pygame.mixer.Sound("Sounds\\miss\\bonk.mp3")


# =========================
# 🤖 Modell laden
# =========================
model = joblib.load("beerpong_model.pkl")

# =========================
# 🔊 Audio Queue
# =========================
audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())


# =========================
# 🎼 Feature Extraction
# =========================
def extract_features(audio, sr):
    y = np.array(audio)

    # trim
    y, _ = librosa.effects.trim(y, top_db=30)

    target_length = int(0.5 * sr)

    if len(y) > target_length:
        y = y[:target_length]
    else:
        y = np.pad(y, (0, target_length - len(y)))

    y = librosa.util.normalize(y)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))

    features = np.concatenate([
        mfcc_mean,
        mfcc_std,
        [centroid],
        [bandwidth],
        [zcr]
    ])

    return features


# =========================
# 🎤 LIVE LOOP
# =========================
def live_classification():
    print("🎤 Live-Klassifikation gestartet... (Strg+C zum Beenden)")

    pre_buffer = []
    pre_buffer_size = int(PRE_BUFFER * SAMPLE_RATE)

    recording = False
    recorded_audio = []

    cooldown_counter = 0

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        blocksize=1024
    ):
        while True:
            data = audio_queue.get().flatten()

            # Cooldown runterzählen
            if cooldown_counter > 0:
                cooldown_counter -= len(data) / SAMPLE_RATE

            # Pre-buffer
            pre_buffer.extend(data)
            if len(pre_buffer) > pre_buffer_size:
                pre_buffer = pre_buffer[-pre_buffer_size:]

            rms = np.sqrt(np.mean(data**2))

            if not recording and cooldown_counter <= 0:
                if rms > THRESHOLD:
                    print("\n🎯 Trigger!")
                    recording = True
                    recorded_audio = pre_buffer.copy()

            elif recording:
                recorded_audio.extend(data)

                if len(recorded_audio) > SAMPLE_RATE * MAX_DURATION:
                    recording = False

                    audio_np = np.array(recorded_audio)

                    # 🧠 Feature + Prediction
                    features = extract_features(audio_np, SAMPLE_RATE)

                    proba = model.predict_proba([features])[0]
                    label = model.classes_[np.argmax(proba)]
                    confidence = np.max(proba)

                    # 🎯 Entscheidung
                    if confidence < CONFIDENCE_THRESHOLD:
                        print(f"🤷 Ignore ({confidence:.2f})")
                    else:
                        print(f"🎯 {label.upper()} ({confidence:.2f})")

                        if label == "hit":
                            hit_sound.play()
                        elif label == "miss":
                            miss_sound.play()

                        cooldown_counter = COOLDOWN

                    recorded_audio = []


# =========================
# ▶️ MAIN
# =========================
if __name__ == "__main__":
    try:
        live_classification()
    except KeyboardInterrupt:
        print("\n👋 Beendet")