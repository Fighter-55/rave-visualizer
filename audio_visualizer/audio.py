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
        self.chroma = chroma          # shape (12, frames), bereits 0..1 pro Spalte
        self.noisiness = noisiness
        self.rolloff = rolloff

    def _index(self, t, length):
        idx = int((t * self.sr) / self.hop_length)
        return max(0, min(idx, length - 1))

    def energy_at(self, t):
        """Lautstaerke-Huellkurve, 0..1. Fuer kontinuierliches 'Atmen'."""
        return float(self.rms[self._index(t, len(self.rms))])

    def onset_at(self, t):
        """Allgemeine Angriffsstaerke, 0..1."""
        return float(self.onset[self._index(t, len(self.onset))])

    def brightness_at(self, t):
        """Spectral Centroid, 0..1. Hoch = hell/hoehenreich."""
        return float(self.centroid[self._index(t, len(self.centroid))])

    def percussive_onset_at(self, t):
        """Onset-Staerke NUR des perkussiven Signalanteils (Drums/Hits)."""
        return float(self.percussive_onset[self._index(t, len(self.percussive_onset))])

    def harmonic_energy_at(self, t):
        """RMS-Energie NUR des harmonischen Signalanteils (Akkorde/Pads/Melodie)."""
        return float(self.harmonic_energy[self._index(t, len(self.harmonic_energy))])

    def chroma_at(self, t):
        """12-elementiger Vektor (C, C#, D, ... B) der Tonhoehen-Energie, 0..1."""
        idx = self._index(t, self.chroma.shape[1])
        return self.chroma[:, idx]

    def noisiness_at(self, t):
        """Zero-Crossing-Rate, 0..1. Hoch bei Rauschen/Hi-Hats/Zischlauten."""
        return float(self.noisiness[self._index(t, len(self.noisiness))])

    def rolloff_at(self, t):
        """Spectral Rolloff, 0..1. Hoch bei viel Energie in hohen Frequenzen."""
        return float(self.rolloff[self._index(t, len(self.rolloff))])


def analyze(filepath, progress_callback=None):
    def progress(message, step, total):
        if progress_callback:
            progress_callback(message, step, total)

    total_steps = 6

    progress("Loading audio file...", 1, total_steps)
    print(f"Loading audio file: {filepath}")
    y, sr = librosa.load(filepath)

    progress("Detecting BPM and beats...", 2, total_steps)
    print("Analyzing BPM and beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo.item())
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    print(f"Detected BPM: {tempo:.1f}")
    print(f"Found {len(beat_times)} beats")

    progress("Separating harmonic and percussive...", 3, total_steps)
    print("Separating harmonic/percussive components...")
    y_harmonic, y_percussive = librosa.effects.hpss(y)

    progress("Analyzing energy, onset and timbre...", 4, total_steps)
    print("Analyzing energy, onset strength and timbre...")
    hop_length = 512
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    percussive_onset = librosa.onset.onset_strength(y=y_percussive, sr=sr, hop_length=hop_length)
    harmonic_rms = librosa.feature.rms(y=y_harmonic, hop_length=hop_length)[0]

    progress("Analyzing chroma and treble...", 5, total_steps)
    print("Analyzing chroma (Tonhoehen) and treble content...")
    chroma = librosa.feature.chroma_stft(y=y_harmonic, sr=sr, hop_length=hop_length)
    chroma_norm = chroma / (chroma.max(axis=0, keepdims=True) + 1e-6)
    zcr = librosa.feature.zero_crossing_rate(y=y, hop_length=hop_length)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=hop_length)[0]

    progress("Finalizing...", 6, total_steps)
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

    return tempo, beat_times, audio_features


if __name__ == "__main__":
    tempo, beat_times, audio_features = analyze("test.mp3")
    print(beat_times[:10])
    print("Energy@1s:", audio_features.energy_at(1.0))
    print("Percussive onset@1s:", audio_features.percussive_onset_at(1.0))
    print("Harmonic energy@1s:", audio_features.harmonic_energy_at(1.0))
    print("Chroma@1s:", audio_features.chroma_at(1.0))
