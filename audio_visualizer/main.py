from menu import run_menu
from visualizer import run

tempo, beat_times, filepath = run_menu()

if tempo is not None:
    run(tempo, beat_times, filepath)