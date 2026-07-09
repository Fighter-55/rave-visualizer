import pygame
import time
from mandala import MandalaVisualizer
from organic_blobs import BlobVisualizer
from stage_visualizer import AdvancedStageVisualizer


def run(tempo, beat_times, filepath, mode="mandala", colors=None, audio_features=None, width=1280, height=800):
    pygame.init()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Rave Visualizer – {tempo:.1f} BPM [{mode.upper()}]")

    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    if mode == "blobs":
        visualizer = BlobVisualizer(width, height, palette=colors)
    elif mode == "stage":
        visualizer = AdvancedStageVisualizer(width, height, palette=colors)
    else:
        visualizer = MandalaVisualizer(width, height, palette=colors)

    pygame.mixer.init()
    try:
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Audio error: {e}")
        return

    clock = pygame.time.Clock()
    start_time = time.time()
    beat_index = 0
    onset_cooldown = 0.0
    running = True

    while running:
        dt = max(0.001, clock.tick(60) / 1000.0)
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if audio_features is not None:
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
        else:
            features = {
                "energy": 0.4, "onset": 0.0, "brightness": 0.4,
                "percussive": 0.0, "harmonic": 0.3,
                "chroma": [0.0] * 12, "noisiness": 0.2, "rolloff": 0.3,
            }

        # Beat detection
        if beat_index < len(beat_times) and t >= beat_times[beat_index]:
            if mode == "mandala":
                visualizer.spawn_ripple(t)
            elif mode == "blobs":
                visualizer.on_beat(strength=1.0 + features["energy"])
            beat_index += 1

        # Onset micro pulses for blobs
        if mode == "blobs":
            onset_cooldown -= dt
            if onset_cooldown <= 0 and features["onset"] > 0.55:
                visualizer.micro_pulse(strength=features["onset"] * 0.6)
                onset_cooldown = 0.06

        # Sparks for mandala
        if mode == "mandala":
            visualizer.maybe_spawn_sparks(t, max(features["rolloff"], features["noisiness"]))

        # Draw
        if mode == "blobs":
            breathing = 1.0 + features["energy"] * 0.22
            speed_mult = 0.6 + features["brightness"] * 1.4
            fade = pygame.Surface((width, height))
            fade.set_alpha(45)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
            visualizer.update(dt)
            visualizer.draw(screen, t, breathing=breathing, speed_mult=speed_mult)

        elif mode == "stage":
            fade = pygame.Surface((width, height))
            fade.set_alpha(40)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
            visualizer.update_and_draw(screen, t, dt, features)

        else:  # mandala
            screen.fill((6, 4, 12))
            visualizer.draw(screen, t, dt, features)

        pygame.display.flip()

    pygame.quit()
