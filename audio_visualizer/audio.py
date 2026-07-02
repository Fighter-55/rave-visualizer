import librosa

def analyze(filepath):
    print(f"Loading audio file: {filepath}")
    y, sr = librosa.load(filepath)

    print("Analyzing BPM and beats...")
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo.item())

    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    print(f"Detected BPM: {tempo:.1f}")
    print(f"Found {len(beat_times)} beats")

    return float(tempo), beat_times

if __name__ == "__main__":
    tempo, beat_times = analyze("test.mp3")
    print(beat_times[:10])