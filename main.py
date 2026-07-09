from menu import run_menu
from visualizer import run as run_file_visualizer
from live_visualizer import run_live as run_live_visualizer

# Holt alle getroffenen Entscheidungen ab
tempo, beat_times, audio_features, filepath, audio_source, visual_mode, chosen_colors = run_menu()

# Überprüft, ob der Modus einer der drei gültigen Optionen entspricht
if visual_mode in ["mandala", "fluid", "stage"]:
    if audio_source == "file" and filepath is not None:
        # Startet den Datei-Visualisierer mit dem gewählten Preset
        run_file_visualizer(tempo, beat_times, audio_features, filepath, mode=visual_mode, colors=chosen_colors)
    elif audio_source == "live":
        # Startet das Live-Mikrofon mit dem gewählten Preset
        run_live_visualizer(mode=visual_mode, colors=chosen_colors)