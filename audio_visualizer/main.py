from menu import run_menu
from visualizer import run

tempo, beat_times, filepath, mode = run_menu()

if mode == "file" and tempo is not None:
    run(tempo, beat_times, filepath)
elif mode == "live":
    print("Live mode coming soon!")