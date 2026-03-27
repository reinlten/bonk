import os
import librosa
import soundfile as sf

# =========================
# ⚙️ KONFIG
# =========================
INPUT_FILE = "ML_idea\\sample_input\\1m_nomusic_full_26_3_26_13_34_hit.wav"
OUTPUT_DIR = "ML_idea\\samples_hit"
SAMPLE_RATE = 48000

# Wie empfindlich die Stille-Erkennung ist
TOP_DB = 30  # kleiner = mehr Segmente

# Mindestlänge eines Segments (in Sekunden)
MIN_DURATION = 0.1

# Padding vor/nach jedem Sample (Sekunden)
PADDING = 0.05


# =========================
# 🚀 HAUPTFUNKTION
# =========================
def extract_samples():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("📥 Lade Audio...")
    y, sr = librosa.load(INPUT_FILE, sr=SAMPLE_RATE)

    print("🔍 Suche nach Events...")
    intervals = librosa.effects.split(y, top_db=TOP_DB)

    print(f"Gefundene Segmente: {len(intervals)}")

    sample_count = 0

    for i, (start, end) in enumerate(intervals):
        duration = (end - start) / sr

        if duration < MIN_DURATION:
            continue

        # Padding hinzufügen
        pad = int(PADDING * sr)
        start_padded = max(0, start - pad)
        end_padded = min(len(y), end + pad)

        segment = y[start_padded:end_padded]

        sample_count += 1
        filename = os.path.join(OUTPUT_DIR, f"sample_{sample_count:03d}.wav")

        sf.write(filename, segment, sr)

    print(f"✅ {sample_count} Samples gespeichert in '{OUTPUT_DIR}'")


# =========================
# ▶️ MAIN
# =========================
if __name__ == "__main__":
    extract_samples()