import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib

# =========================
# ⚙️ KONFIGURATION
# =========================
DATASET = {
    "hit": "ML_idea\\samples_hit_training",
    "miss": "ML_idea\\samples_miss_training"
}

SAMPLE_RATE = 48000
TARGET_DURATION = 0.5
N_MFCC = 13

# =========================
# 🎼 FEATURE EXTRAKTION
# =========================
def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE)

    # Stille entfernen
    y, _ = librosa.effects.trim(y, top_db=30)

    # Fixe Länge
    target_length = int(TARGET_DURATION * sr)

    if len(y) > target_length:
        y = y[:target_length]
    else:
        y = np.pad(y, (0, target_length - len(y)))

    # Normalisieren
    y = librosa.util.normalize(y)

    # MFCC
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    # Zusatzfeatures
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
# 📁 DATEN LADEN
# =========================
def load_dataset():
    X = []
    y = []

    for label, folder in DATASET.items():
        print(f"📂 Lade {label} aus {folder}")

        for file in os.listdir(folder):
            if file.endswith(".wav"):
                path = os.path.join(folder, file)

                try:
                    features = extract_features(path)
                    X.append(features)
                    y.append(label)
                except Exception as e:
                    print(f"⚠ Fehler bei {file}: {e}")

    return np.array(X), np.array(y)


# =========================
# 🚀 TRAINING
# =========================
def train():
    print("📥 Lade Daten...")
    X, y = load_dataset()

    print(f"\nSamples gesamt: {len(X)}")
    print(f"Feature-Dimension: {X.shape[1]}")

    # Check Balance
    unique, counts = np.unique(y, return_counts=True)
    print("\n📊 Klassenverteilung:")
    for u, c in zip(unique, counts):
        print(f"{u}: {c}")

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Pipeline
    model = make_pipeline(
        StandardScaler(),
        SVC(kernel="rbf", probability=True)
    )

    print("\n🤖 Trainiere Modell...")
    model.fit(X_train, y_train)

    print("\n📊 Evaluierung...")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Confidence Analyse
    probas = model.predict_proba(X_test)
    confidences = np.max(probas, axis=1)

    print("\n🔍 Confidence:")
    print(f"Min: {confidences.min():.3f}")
    print(f"Mean: {confidences.mean():.3f}")
    print(f"Max: {confidences.max():.3f}")

    # Modell speichern
    joblib.dump(model, "beerpong_model.pkl")
    print("\n💾 Modell gespeichert als beerpong_model.pkl")


# =========================
# ▶️ MAIN
# =========================
if __name__ == "__main__":
    train()