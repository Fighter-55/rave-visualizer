import pygame
import time
import math

# Alle Visualizer Module importieren
import organic_blobs
from stage_visualizer import AdvancedStageVisualizer
from grid_visualizer import Grid3DVisualizer
from mandala import MandalaVisualizer
from flower_visualizer import FlowerVisualizer
import color_menu  # Unser Echtzeit-Overlay-Modul


class AudioFeatures:
    def energy_at(self, t): return 0.3

    def onset_at(self, t): return 0.0

    def brightness_at(self, t): return 0.4


def create_visualizer_instance(mode, width, height, colors):
    if mode == "blobs":
        return organic_blobs.BlobVisualizer(width, height, palette=colors)
    elif mode == "stage":
        return AdvancedStageVisualizer(width, height, palette=colors)
    elif mode == "grid":
        return Grid3DVisualizer(width, height, palette=colors)
    elif mode == "mandala":
        return MandalaVisualizer(width, height, palette=colors)
    elif mode == "flower":
        return FlowerVisualizer(width, height, palette=colors)
    return organic_blobs.BlobVisualizer(width, height, palette=colors)


def run(tempo, beat_times, filepath, mode="blobs", audio_features=None, colors=None, width=1280, height=800):
    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]
    if audio_features is None:
        audio_features = AudioFeatures()

    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Audio-Fehler: {e}")

    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(f"Rave Visualizer - {mode.upper()}")
    clock = pygame.time.Clock()

    current_mode = mode
    current_palette_name = "Neon Rave"
    visualizer = create_visualizer_instance(current_mode, width, height, colors)

    start_time = time.time()
    beat_index = 0
    onset_cooldown = 0.0

    show_menu = False
    running = True

    while running:
        dt = max(0.001, clock.tick(60) / 1000.0)
        t = (time.time() - start_time)

        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    show_menu = not show_menu

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if show_menu:
                    old_p, old_m = current_palette_name, current_mode
                    current_palette_name, current_mode = color_menu.check_overlay_clicks(
                        mx, my, width, height, current_palette_name, current_mode
                    )

                    if current_palette_name != old_p or current_mode != old_m:
                        new_colors = color_menu.PRESET_PALETTES[current_palette_name]
                        visualizer = create_visualizer_instance(current_mode, width, height, new_colors)
                        pygame.display.set_caption(f"Rave Visualizer - {current_mode.upper()}")

        # Audio-Features lesen
        features = {
            "energy": audio_features.energy_at(t),
            "onset": audio_features.onset_at(t),
            "brightness": audio_features.brightness_at(t) if hasattr(audio_features, 'brightness_at') else 0.4,
            "percussive": audio_features.onset_at(t),
            "chroma": audio_features.chroma[:, audio_features._index(t, audio_features.chroma.shape[1])] if hasattr(
                audio_features, 'chroma') else [0.0] * 12
        }

        # Beat-Trigger
        if beat_index < len(beat_times) and t >= beat_times[beat_index]:
            if current_mode == "mandala" and hasattr(visualizer, 'spawn_ripple'):
                visualizer.spawn_ripple(t)
            elif hasattr(visualizer, 'on_beat'):
                visualizer.on_beat(strength=1.0 + features["energy"])
            beat_index += 1

        # Onset-Filter
        onset_cooldown -= dt
        if onset_cooldown <= 0 and features["onset"] > 0.55:
            if hasattr(visualizer, 'micro_pulse'):
                visualizer.micro_pulse(strength=features["onset"])
            onset_cooldown = 0.05

        # Trail-Effekt rendern
        trail_surf = pygame.Surface((width, height))
        trail_surf.set_alpha(35 if current_mode in ["flower", "stage", "grid"] else 45)
        trail_surf.fill((6, 4, 12) if current_mode in ["flower", "mandala"] else (0, 0, 0))
        screen.blit(trail_surf, (0, 0))

        # --- ABSTURZSICHERE RENDERING-WEICHE ---
        # Jedes Modul kocht sein eigenes Süppchen bei den Funktionsnamen.
        # Hier prüfen wir dynamisch, was die geladene Klasse anbietet.

        if current_mode == "blobs":
            breathing = 1.0 + features["energy"] * 0.25
            speed_mult = 0.5 + features["onset"] * 1.5
            if hasattr(visualizer, 'update'): visualizer.update(dt)
            if hasattr(visualizer, 'draw'): visualizer.draw(screen, t, breathing=breathing, speed_mult=speed_mult)

        elif current_mode == "mandala":
            if hasattr(visualizer, 'update'): visualizer.update(dt)
            if hasattr(visualizer, 'draw'): visualizer.draw(screen, t, pulse_strength=features["energy"])

        else:
            # Für Flower, Stage, Grid3D
            if hasattr(visualizer, 'update_and_draw'):
                visualizer.update_and_draw(screen, t, dt, features)

        # 2. OVERLAY DARÜBER ZEICHNEN (Falls 'M' aktiv ist)
        if show_menu:
            color_menu.draw_live_overlay(screen, width, height, current_palette_name, current_mode)

        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()