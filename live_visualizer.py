import pygame
import time
import math
import live_audio
from mandala import MandalaVisualizer
from organic_blobs import BlobVisualizer  # KORRIGIERT
from stage_visualizer import AdvancedStageVisualizer

BASS_THRESHOLD = 500000

def run_live(mode="mandala", colors=None):
    pygame.init()

    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Rave Visualizer – Live {mode.upper()}")

    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    if mode == "fluid":
        visualizer = BlobVisualizer(WIDTH, HEIGHT, palette=colors)  # KORRIGIERT
    elif mode == "stage":
        visualizer = AdvancedStageVisualizer(WIDTH, HEIGHT, palette=colors)
    else:
        visualizer = MandalaVisualizer(WIDTH, HEIGHT, palette=colors)

    clock = pygame.time.Clock()
    p, stream = live_audio.open_stream()
    start_time = time.time()
    trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        bass, mid, treble = live_audio.get_frequency_bands(stream)

        live_energy = max(0.1, min(1.0, bass / 1200000.0))
        live_brightness = max(0.1, min(1.0, treble / 400000.0))
        live_percussive = 0.8 if bass > BASS_THRESHOLD else 0.1

        features = {
            "energy": live_energy,
            "brightness": live_brightness,
            "percussive": live_percussive,
            "onset": live_percussive,
            "harmonic": max(0.1, min(1.0, 1.0 - live_brightness)),
            "chroma": [max(0.0, math.sin(t + i * 0.5) * live_energy) for i in range(12)],
            "noisiness": max(0.1, min(1.0, treble / 500000.0)),
            "rolloff": max(0.1, min(1.0, mid / 500000.0))
        }

        if bass > BASS_THRESHOLD:
            if hasattr(visualizer, 'spawn_ripple'):
                visualizer.spawn_ripple(t)
            if hasattr(visualizer, 'on_beat'):
                visualizer.on_beat(1.0 + live_energy)

        if mode == "fluid":
            trail_surf.fill((6, 4, 12, 16))
            visualizer.update(dt)
            visualizer.draw(trail_surf, t, breathing=(1.0 + live_energy * 0.22), speed_mult=(0.6 + live_brightness * 1.4))
            screen.blit(trail_surf, (0, 0))
        elif mode == "stage":
            screen.fill((10, 10, 15))
            visualizer.update_and_draw(screen, t, dt, features)
        else:
            trail_surf.fill((10, 8, 18, 24))
            visualizer.update_and_draw(trail_surf, t, dt, features)
            screen.blit(trail_surf, (0, 0))

        pygame.display.flip()

    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()