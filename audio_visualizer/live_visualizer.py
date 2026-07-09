import pygame
import time
import math
import live_audio
from mandala import MandalaVisualizer
from organic_blobs import BlobVisualizer
from stage_visualizer import AdvancedStageVisualizer
from grid_visualizer import Grid3DVisualizer
from flower_visualizer import FlowerVisualizer  # Import des neuen Moduls

BASS_THRESHOLD = 500000

def run_live(mode="mandala", colors=None):
    pygame.init()

    screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption(f"Rave Visualizer – Live {mode.upper()}")

    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    # Zuweisung des Live-Visualizers inklusive Flower
    if mode == "blobs":
        visualizer = BlobVisualizer(WIDTH, HEIGHT, palette=colors)
    elif mode == "stage":
        visualizer = AdvancedStageVisualizer(WIDTH, HEIGHT, palette=colors)
    elif mode == "grid":
        visualizer = Grid3DVisualizer(WIDTH, HEIGHT, palette=colors)
    elif mode == "flower":
        visualizer = FlowerVisualizer(WIDTH, HEIGHT, palette=colors)
    else:
        visualizer = MandalaVisualizer(WIDTH, HEIGHT, palette=colors)

    clock = pygame.time.Clock()
    p, stream = live_audio.open_stream()
    start_time = time.time()

    running = True
    while running:
        dt = max(0.001, clock.tick(60) / 1000.0)
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        try:
            bass, mid, treble = live_audio.get_frequency_bands(stream)
        except Exception:
            bass, mid, treble = 0, 0, 0

        # Normalisierung der Live-Werte
        live_energy = min(1.0, (bass + mid) / 1200000.0)
        live_brightness = min(1.0, treble / 400000.0)
        live_onset = 1.0 if bass > BASS_THRESHOLD else 0.0

        features = {
            "energy": live_energy,
            "onset": live_onset,
            "brightness": live_brightness,
            "percussive": live_onset,
            "chroma": [0.0] * 12
        }

        # Trigger Beat Events
        if bass > BASS_THRESHOLD:
            if mode == "mandala":
                visualizer.spawn_ripple(t)
            elif mode == "blobs" or mode == "flower":
                visualizer.on_beat(strength=1.0 + live_energy)

        # Render-Modus abarbeiten
        if mode == "blobs":
            breathing = 1.0 + live_energy * 0.22
            speed_mult = 0.6 + live_brightness * 1.4
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.set_alpha(45)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
            visualizer.update(dt)
            visualizer.draw(screen, t, breathing=breathing, speed_mult=speed_mult)

        elif mode == "stage":
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.set_alpha(40)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
            visualizer.update_and_draw(screen, t, dt, features)

        elif mode == "grid":
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.set_alpha(40)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
            visualizer.update_and_draw(screen, t, dt, features)

        elif mode == "flower":
            # Sanfter Trail-Effekt für die Fäden im Live-Modus
            fade = pygame.Surface((WIDTH, HEIGHT))
            fade.set_alpha(35)
            fade.fill((6, 4, 12))
            screen.blit(fade, (0, 0))
            visualizer.update_and_draw(screen, t, dt, features)

        else:  # mandala
            screen.fill((6, 4, 12))
            visualizer.update(dt)
            visualizer.draw(screen, t, pulse_strength=live_energy)

        pygame.display.flip()

    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()