from menu import run_menu
from visualizer import run
from live_visualizer import run_live
import color_menu

tempo, beat_times, audio_features, filepath, mode, visual_mode, colors = run_menu()


if colors is None:
    colors = color_menu.PRESET_PALETTES["Neon Rave"]

if mode == "file" and tempo is not None:
    run(tempo, beat_times, filepath, mode=visual_mode, audio_features=audio_features, colors=colors, width=1280, height=800)
elif mode == "live":
    run_live(mode=visual_mode, colors=colors)