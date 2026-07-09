import pygame
import math
import random
import time
import os

# Imports aller verfügbaren Visualisierungs-Klassen
from mandala import MandalaVisualizer
from grid_visualizer import Grid3DVisualizer

# Dynamische Imports mit Fallbacks für optionale Dateien
try:
    from organic_blobs import BlobVisualizer
except ImportError:
    try:
        from fluid_clouds import FluidCloudVisualizer as BlobVisualizer
    except ImportError:
        BlobVisualizer = None

try:
    from stage_visualizer import AdvancedStageVisualizer
except ImportError:
    AdvancedStageVisualizer = None


def run(tempo, beat_times, filepath=None, mode="mandala", audio_features=None, colors=None, width=1280, height=800):
    pygame.init()
    pygame.mixer.init()

    # Audio-Datei laden und abspielen, falls übergeben
    if filepath and os.path.exists(filepath):
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

    WIDTH, HEIGHT = width, height
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(f"Rave Visualizer – {mode.upper()} Mode")

    # Standard-Farbpalette setzen, falls keine übergeben wurde
    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    # --- SAUBERE INITIALISIERUNG DER GRAFIK-KLASSE ---
    if mode == "grid":
        visualizer = Grid3DVisualizer(WIDTH, HEIGHT, palette=colors)
    elif mode == "stage" and AdvancedStageVisualizer is not None:
        visualizer = AdvancedStageVisualizer(WIDTH, HEIGHT, palette=colors)
    elif (mode == "blobs" or mode == "fluid") and BlobVisualizer is not None:
        visualizer = BlobVisualizer(WIDTH, HEIGHT, palette=colors)
    else:
        # Fallback auf Mandala, falls eine Klasse fehlt oder ausgewählt wurde
        visualizer = MandalaVisualizer(WIDTH, HEIGHT, palette=colors)

    clock = pygame.time.Clock()
    start_time = time.time()
    beat_index = 0
    trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    running = True
    while running:
        # dt = Delta-Time (Zeit seit dem letzten Frame in Sekunden)
        dt = max(0.001, clock.tick(60) / 1000.0)
        t = time.time() - start_time

        # Pygame Events abfangen (Fenster schließen, Größe ändern)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        # 1. Musikalische Features auslesen (mit sicherem Fallback-Dict)
        if audio_features:
            try:
                features = {
                    "energy": audio_features.energy_at(t),
                    "onset": audio_features.onset_at(t),
                    "brightness": audio_features.brightness_at(t),
                    "percussive": audio_features.percussive_onset_at(t),
                    "harmonic": audio_features.harmonic_energy_at(t),
                    "chroma": audio_features.chroma_at(t),
                    "noisiness": audio_features.noisiness_at(t),
                    "rolloff": audio_features.rolloff_at(t),
                }
            except Exception:
                features = {
                    "energy": 0.3, "onset": 0.0, "brightness": 0.4,
                    "percussive": 0.15, "harmonic": 0.4, "chroma": [0.0] * 12,
                    "noisiness": 0.2, "rolloff": 0.3
                }
        else:
            features = {
                "energy": 0.3, "onset": 0.0, "brightness": 0.4,
                "percussive": 0.15, "harmonic": 0.4, "chroma": [0.0] * 12,
                "noisiness": 0.2, "rolloff": 0.3
            }

        # 2. NumPy-Array sicherer Beat-Trigger (verhindert Truth-Value-Error)
        if beat_times is not None and len(beat_times) > 0 and beat_index < len(beat_times) and t >= beat_times[
            beat_index]:
            if mode == "mandala" and hasattr(visualizer, 'spawn_ripple'):
                visualizer.spawn_ripple(t)
            elif mode == "blobs" and hasattr(visualizer, 'on_beat'):
                visualizer.on_beat(strength=1.0 + features["energy"])
            beat_index += 1

        # 3. GRAFIK RENDERN NACH MODUS
        if mode == "grid":
            screen.fill((6, 4, 12))  # Hintergrund dunkel füllen
            visualizer.update_and_draw(screen, t, dt, features)

        elif mode == "blobs" or mode == "fluid":
            # Motion-Blur / Schweif-Effekt für die organischen Formen
            trail_surf.fill((6, 4, 12, 15))
            visualizer.update_and_draw(trail_surf, t, dt, features)
            screen.blit(trail_surf, (0, 0))

        else:
            # Für Mandala und Stage Mode
            screen.fill((6, 4, 12))
            if hasattr(visualizer, 'draw'):
                visualizer.draw(screen, t, dt, features)
            elif hasattr(visualizer, 'update_and_draw'):
                visualizer.update_and_draw(screen, t, dt, features)

        pygame.display.flip()

    pygame.quit()