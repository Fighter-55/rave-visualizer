from audio import analyze
from visualizer import run

filepath = "test.mp3"
tempo, beat_times = analyze(filepath)
run(tempo, beat_times, filepath)