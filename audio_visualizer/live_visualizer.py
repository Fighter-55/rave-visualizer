import pygame
import time
import math
import live_audio
from mandala import MandalaVisualizer
from organic_blobs import BlobVisualizer
from stage_visualizer import AdvancedStageVisualizer
from grid_visualizer import Grid3DVisualizer
from flower_visualizer import FlowerVisualizer
import color_menu

BASS_THRESHOLD = 500000


def create_visualizer_instance(mode, width, height, colors):
    try:
        if mode == "blobs":
            return BlobVisualizer(width, height, palette=colors)
        elif mode == "stage":
            return AdvancedStageVisualizer(width, height, palette=colors)
        elif mode == "grid":
            return Grid3DVisualizer(width, height, palette=colors)
        elif mode == "mandala":
            return MandalaVisualizer(width, height, palette=colors)
        elif mode == "flower":
            return FlowerVisualizer(width, height, palette=colors)
    except Exception as e:
        print(f"[LIVE BRIDGE] Fehler bei Engine '{mode}': {e}")
    return BlobVisualizer(width, height, palette=colors)


def run_live(mode="mandala", colors=None):
    pygame.init()

    screen = pygame.display.set_mode((1280, 800), pygame.RESIZABLE)
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption(f"Rave Visualizer – Live Microphone Engine")

    if colors is None:
        colors = color_menu.PRESET_PALETTES["Neon Rave"]

    current_mode = mode
    current_palette_name = "Neon Rave"
    current_colors = colors
    visualizer = create_visualizer_instance(current_mode, WIDTH, HEIGHT, current_colors)

    clock = pygame.time.Clock()

    # Mikrofon-Stream öffnen
    try:
        p, stream = live_audio.open_stream()
    except Exception as stream_error:
        print(f"[LIVE CRITICAL] Mikrofon konnte nicht geöffnet werden! {stream_error}")
        return

    start_time = time.time()
    sidebar_active = False

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        t = time.time() - start_time
        WIDTH, HEIGHT = screen.get_size()

        # --- AUTO-OPEN SIDEBAR (Maus am rechten Rand) ---
        mx, my = pygame.mouse.get_pos()
        if mx > WIDTH - 60:
            sidebar_active = True
        elif sidebar_active and mx < WIDTH - (color_menu.SIDEBAR_WIDTH + 40):
            sidebar_active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                visualizer = create_visualizer_instance(current_mode, WIDTH, HEIGHT, current_colors)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    sidebar_active = not sidebar_active

            # Live-Echtzeit-Wechsel über Sidebar
            if sidebar_active:
                new_mode, new_pal_name = color_menu.handle_menu_events(
                    event, current_mode, current_palette_name, screen_width=WIDTH
                )
                if new_mode and new_mode != current_mode:
                    current_mode = new_mode
                    visualizer = create_visualizer_instance(current_mode, WIDTH, HEIGHT, current_colors)
                if new_pal_name:
                    current_palette_name = new_pal_name
                    current_colors = color_menu.PRESET_PALETTES[new_pal_name]
                    visualizer = create_visualizer_instance(current_mode, WIDTH, HEIGHT, current_colors)

        # Frequenzen abfragen
        try:
            bass, mid, treble = live_audio.get_frequency_bands(stream)
        except Exception:
            bass, mid, treble = 100000, 100000, 100000

        # Normalisierungsbrücke für Live-Mikrofon-Daten
        live_energy = max(0.1, min(1.0, bass / 1200000.0))
        live_brightness = max(0.1, min(1.0, treble / 400000.0))
        live_percussive = 0.8 if bass > BASS_THRESHOLD else 0.1

        # Mappen auf das einheitliche Feature-Wörterbuch
        features = {
            "energy": live_energy,
            "brightness": live_brightness,
            "percussive": live_percussive,
            "harmonic": max(0.1, min(1.0, 1.0 - live_brightness)),
            "chroma": [max(0.0, math.sin(t + i * 0.5) * live_energy) for i in range(12)],
            "noisiness": max(0.1, min(1.0, treble / 500000.0)),
            "rolloff": max(0.1, min(1.0, mid / 500000.0)),
            "onset": live_percussive
        }

        # Beat-Events simulieren
        if live_percussive > 0.5:
            if hasattr(visualizer, "on_beat"): visualizer.on_beat(1.2)
            if hasattr(visualizer, "micro_pulse"): visualizer.micro_pulse(0.6)
            if hasattr(visualizer, "spawn_ripple"): visualizer.spawn_ripple(t)

        # Hintergrund zeichnen
        trail_surf = pygame.Surface((WIDTH, HEIGHT))
        trail_surf.set_alpha(35 if current_mode in ["flower", "stage", "grid"] else 45)
        trail_surf.fill((6, 4, 12) if current_mode in ["flower", "mandala"] else (0, 0, 0))
        screen.blit(trail_surf, (0, 0))

        # --- LIVE RENDERING-BRÜCKE ---
        try:
            if current_mode == "blobs":
                breathing = 1.0 + live_energy * 0.22
                speed_mult = 0.6 + live_brightness * 1.4
                if hasattr(visualizer, 'update'): visualizer.update(dt)
                if hasattr(visualizer, 'draw'): visualizer.draw(screen, t, breathing=breathing, speed_mult=speed_mult)
            else:
                if hasattr(visualizer, "update_and_draw"):
                    visualizer.update_and_draw(screen, t, dt, features)
        except Exception as live_render_error:
            print(f"[LIVE BRIDGE CRITICAL] Engine abgestürzt, wechsle zu Blobs: {live_render_error}")
            current_mode = "blobs"
            visualizer = create_visualizer_instance(current_mode, WIDTH, HEIGHT, current_colors)

        # Sidebar rendern
        if sidebar_active:
            color_menu.draw_menu(screen, current_mode, current_palette_name)

        pygame.display.flip()

    try:
        stream.stop_stream()
        stream.close()
        p.terminate()
    except:
        pass
    pygame.quit()