from menu import run_menu
from visualizer import run
from live_visualizer import run_live

tempo, beat_times, audio_features, filepath, mode = run_menu()

if mode == "file" and tempo is not None:
    run(tempo, beat_times, filepath, mode="mandala", audio_features=audio_features, width=1280, height=800)
elif mode == "live":
    run_live()
