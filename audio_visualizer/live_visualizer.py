import pygame
import time
import math
import live_audio
from mandala import MandalaVisualizer
from organic_blobs import BlobVisualizer
from stage_visualizer import AdvancedStageVisualizer
from grid_visualizer import Grid3DVisualizer


BASS_THRESHOLD = 500000

def run_live(mode="mandala", colors=None):
    pygame.init()

    screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption(f"Rave Visualizer – Live {mode.upper()}")

    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    if mode == "blobs":
        visualizer = BlobVisualizer(WIDTH, HEIGHT, palette=colors)
    elif mode == "stage":
        visualizer = AdvancedStageVisualizer(WIDTH, HEIGHT, palette=colors)
    elif mode == "grid":
        visualizer = Grid3DVisualizer(WIDTH, HEIGHT, palette=colors)
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()

        # Get live frequency bands
        bass, mid, treble = live_audio.get_frequency_bands(stream)

        # Map raw FFT values to normalized 0..1 feature dict
        live_energy     = max(0.1, min(1.0, bass / 1200000.0))
        live_brightness = max(0.1, min(1.0, treble / 400000.0))
        live_percussive = 0.8 if bass > BASS_THRESHOLD else 0.1
        live_mid        = max(0.1, min(1.0, mid / 500000.0))

        features = {
            "energy":     live_energy,
            "brightness": live_brightness,
            "percussive": live_percussive,
            "onset":      live_percussive,
            "harmonic":   max(0.1, min(1.0, 1.0 - live_brightness)),
            "chroma":     [max(0.0, math.sin(t + i * 0.5) * live_energy) for i in range(12)],
            "noisiness":  max(0.1, min(1.0, treble / 500000.0)),
            "rolloff":    live_mid,
        }

        # Trigger beat events on bass spike
        if bass > BASS_THRESHOLD:
            if mode == "mandala":
                visualizer.spawn_ripple(t)
            elif mode == "blobs":
                visualizer.on_beat(strength=1.0 + live_energy)

        # Draw
        if mode == "blobs":
            breathing  = 1.0 + live_energy * 0.22
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

        else:  # mandala
            screen.fill((6, 4, 12))
            visualizer.maybe_spawn_sparks(t, max(features["rolloff"], features["noisiness"]))
            visualizer.draw(screen, t, dt, features)

        pygame.display.flip()

    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()