import librosa
import numpy as np


def _normalize(arr):
    """Skaliert ein Array robust auf den Bereich [0, 1] (Ausreisser-tolerant)."""
    arr = np.asarray(arr, dtype=float)
    lo, hi = np.percentile(arr, 5), np.percentile(arr, 95)
    if hi - lo < 1e-6:
        return np.zeros_like(arr)
    return np.clip((arr - lo) / (hi - lo), 0.0, 1.0)


class AudioFeatures:
    """Gibt schnellen Zugriff auf Feature-Werte zu einem beliebigen
    Zeitpunkt t (Sekunden) waehrend der Wiedergabe."""

    def __init__(self, sr, hop_length, rms, onset, centroid,
                 percussive_onset, harmonic_energy, chroma, noisiness, rolloff):
        self.sr = sr
        self.hop_length = hop_length
        self.rms = rms
        self.onset = onset
        self.centroid = centroid
        self.percussive_onset = percussive_onset
        self.harmonic_energy = harmonic_energy
        self.chroma = chroma  # shape (12, frames), bereits 0..1 pro Spalte
        self.noisiness = noisiness
        self.rolloff = rolloff

    def _index(self, t, length):
        idx = int((t * self.sr) / self.hop_length)
        return max(0, min(idx, length - 1))

    def energy_at(self, t):
        return float(self.rms[self._index(t, len(self.rms))])

    def onset_at(self, t):
        return float(self.onset[self._index(t, len(self.onset))])

    def brightness_at(self, t):
        return float(self.centroid[self._index(t, len(self.centroid))])

    def percussive_onset_at(self, t):
        return float(self.percussive_onset[self._index(t, len(self.percussive_onset))])

    def harmonic_energy_at(self, t):
        return float(self.harmonic_energy[self._index(t, len(self.harmonic_energy))])

    def chroma_at(self, t):
        idx = self._index(t, self.chroma.shape[1])
        return [float(v) for v in self.chroma[:, idx]]

    def noisiness_at(self, t):
        return float(self.noisiness[self._index(t, len(self.noisiness))])

    def rolloff_at(self, t):
        return float(self.rolloff[self._index(t, len(self.rolloff))])


def analyze(filepath, progress_callback=None):
    """
    Analysiert die Audiodatei und meldet Fortschritte (0-100%) über progress_callback.
    """

    def update_progress(percent, status):
        if progress_callback:
            progress_callback(percent, status)

    update_progress(5, "Lade Audiodatei...")
    sr = 22050
    hop_length = 512

    try:
        y, _ = librosa.load(filepath, sr=sr)
    except Exception as e:
        print(f"Fehler beim Laden mit Librosa: {e}")
        return None, None, None

    update_progress(20, "Berechne Tempo und Beat-Struktur...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)

    update_progress(40, "Trenne harmonische & perkussive Frequenzen...")
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    update_progress(60, "Analysiere Onsets und RMS (Lautstärke)...")
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]

    update_progress(75, "Analysiere perkussive Peaks...")
    percussive_onset = librosa.onset.onset_strength(y=y_percussive, sr=sr, hop_length=hop_length)
    harmonic_rms = librosa.feature.rms(y=y_harmonic, hop_length=hop_length)[0]

    update_progress(85, "Analysiere Tonhöhen (Chroma) & Höhenfrequenzen...")
    chroma = librosa.feature.chroma_stft(y=y_harmonic, sr=sr, hop_length=hop_length)
    chroma_norm = chroma / (chroma.max(axis=0, keepdims=True) + 1e-6)

    zcr = librosa.feature.zero_crossing_rate(y=y, hop_length=hop_length)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop_length)[0]

    update_progress(95, "Finalisiere Audio-Features...")
    audio_features = AudioFeatures(
        sr=sr,
        hop_length=hop_length,
        rms=_normalize(rms),
        onset=_normalize(onset_env),
        centroid=_normalize(centroid),
        percussive_onset=_normalize(percussive_onset),
        harmonic_energy=_normalize(harmonic_rms),
        chroma=chroma_norm,
        noisiness=_normalize(zcr),
        rolloff=_normalize(rolloff),
    )

    update_progress(100, "Analyse abgeschlossen!")

    try:
        tempo_float = float(tempo[0])
    except (TypeError, IndexError):
        tempo_float = float(tempo)

    return tempo_float, beat_times, audio_features