import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib


# ⚙️ KONFIGURATION

SAMPLE_RATE = 48000
TARGET_DURATION = 0.5
N_MFCC = 13


def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=SAMPLE_RATE)

    # Stille entfernen
    y, _ = librosa.effects.trim(y, top_db=30)

    # Auf fixe Länge bringen
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


if __name__ == "__main__":
    model = joblib.load("beerpong_model.pkl")

    features = extract_features("ML_idea\\samples_hit_training\\sample_001.wav")

    proba = model.predict_proba([features])[0]
    label = model.classes_[np.argmax(proba)]
    confidence = np.max(proba)
    print(proba)

    if confidence < 0.75:
        print("Ignore")
    else:
        print(label)