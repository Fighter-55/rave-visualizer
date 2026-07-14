import pygame
import time
import math
import os

# Alle Visualizer Module importieren
import organic_blobs
from stage_visualizer import AdvancedStageVisualizer
from grid_visualizer import Grid3DVisualizer
from mandala import MandalaVisualizer
from flower_visualizer import FlowerVisualizer
import color_menu  # Unser Sidebar-Modul


def create_visualizer_instance(mode, width, height, colors):
    """Erzeugt die Instanz der gewünschten Engine."""
    try:
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
    except Exception as e:
        print(f"[BRIDGE WARNING] Fehler beim Erstellen von '{mode}': {e}")

    return organic_blobs.BlobVisualizer(width, height, palette=colors)


def draw_timeline(screen, current_time, total_length):
    """Zeichnet eine wunderschöne, interaktive Zeitleiste am unteren Bildschirmrand."""
    width, height = screen.get_size()
    timeline_y = height - 30

    # Hintergrund-Leiste
    pygame.draw.rect(screen, (20, 15, 30), (0, height - 45, width, 45))
    pygame.draw.line(screen, (80, 50, 150), (0, height - 45), (width, height - 45), 2)

    # Fortschrittsbalken-Schiene
    margin = 30
    bar_width = width - (margin * 2)
    pygame.draw.line(screen, (50, 45, 60), (margin, timeline_y), (margin + bar_width, timeline_y), 4)

    # Berechnen des Fortschritts
    if total_length <= 0:
        total_length = 1.0
    progress = max(0.0, min(1.0, current_time / total_length))
    filled_x = margin + int(progress * bar_width)

    # Gespielter Fortschritt (Neon-Pink/Cyan)
    pygame.draw.line(screen, (0, 255, 255), (margin, timeline_y), (filled_x, timeline_y), 4)
    pygame.draw.circle(screen, (255, 0, 150), (filled_x, timeline_y), 8)

    # Zeitstempel rendern
    font = pygame.font.SysFont("Arial", 14)

    def format_time(seconds):
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"

    time_str = f"{format_time(current_time)} / {format_time(total_length)}"
    txt_surf = font.render(time_str, True, (200, 200, 210))
    screen.blit(txt_surf, (width - txt_surf.get_width() - 20, height - 24))


def run(tempo, beat_times, filepath, mode="blobs", audio_features=None, colors=None, width=1280, height=800):
    if colors is None:
        colors = color_menu.PRESET_PALETTES["Neon Rave"]

    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(f"Rave Visualizer – Playing: {os.path.basename(filepath)}")

    # Musik-Gesamtlänge auslesen
    song_length = 240.0
    try:
        temp_sound = pygame.mixer.Sound(filepath)
        song_length = temp_sound.get_length()
        del temp_sound
    except Exception as e:
        print(f"[TIMELINE ERROR] Konnte Song-Länge nicht ermitteln: {e}")

    # Musik abspielen
    try:
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"[BRIDGE ERROR] Musik-Wiedergabe fehlgeschlagen: {e}")

    current_mode = mode
    current_palette_name = "Neon Rave"
    current_colors = colors
    visualizer = create_visualizer_instance(current_mode, width, height, current_colors)

    clock = pygame.time.Clock()
    start_time = time.time()

    beat_index = 0
    onset_cooldown = 0.0
    sidebar_active = False

    running = True
    while running:
        dt = max(0.001, clock.tick(60) / 1000.0)

        # Multiplikator für Geschwindigkeit holen
        speed_mult = color_menu.PARAMS["Speed"]["val"]
        # Zeit läuft proportional zum Speed-Multiplier!
        t = (time.time() - start_time)

        width, height = screen.get_size()

        # --- AUTO-OPEN SIDEBAR ---
        mx, my = pygame.mouse.get_pos()
        if mx > width - 60:
            sidebar_active = True
        elif sidebar_active and mx < width - (color_menu.SIDEBAR_WIDTH + 40):
            sidebar_active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                visualizer = create_visualizer_instance(current_mode, width, height, current_colors)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    sidebar_active = not sidebar_active

            # Timeline Seek Klick (Klick auf den Balken ganz unten)
            if event.type == pygame.MOUSEBUTTONDOWN and not (sidebar_active and mx >= width - color_menu.SIDEBAR_WIDTH):
                if my >= height - 45:
                    margin = 30
                    bar_width = width - (margin * 2)
                    clicked_frac = (mx - margin) / bar_width
                    clicked_frac = max(0.0, min(1.0, clicked_frac))

                    # Musik-Sekunden-Ziel berechnen
                    target_time = clicked_frac * song_length

                    # Skip ausführen!
                    try:
                        pygame.mixer.music.play(0, target_time)
                        start_time = time.time() - target_time

                        # Beat-Index passend zur neuen Zeit zurücksetzen!
                        beat_index = 0
                        if beat_times is not None and len(beat_times) > 0:
                            while beat_index < len(beat_times) and beat_times[beat_index] < target_time:
                                beat_index += 1
                    except Exception as seek_error:
                        print(f"[TIMELINE SEEK ERROR] Fehler beim Springen: {seek_error}")

            # Sidebar-Events
            if sidebar_active:
                res_mode, res_pal = color_menu.handle_menu_events(
                    event, current_mode, current_palette_name, screen_width=width
                )
                if res_mode == "PARAMS_UPDATED":
                    # Hier reagieren wir auf Parameteränderungen
                    pass
                elif res_mode and res_mode != current_mode:
                    current_mode = res_mode
                    visualizer = create_visualizer_instance(current_mode, width, height, current_colors)
                if res_pal:
                    current_palette_name = res_pal
                    current_colors = color_menu.PRESET_PALETTES[res_pal]
                    visualizer = create_visualizer_instance(current_mode, width, height, current_colors)

        # --- LIVE-PARAMETER AN ENGINE ÜBERTRAGEN ---
        # Falls die Engine "symmetry" oder ähnliche Attribute unterstützt, speisen wir diese hier ein:
        if hasattr(visualizer, 'symmetry'):
            visualizer.symmetry = int(color_menu.PARAMS["Symmetry"]["val"])

        # --- AUDIO-FEATURES MULTIPLIZIERT MIT SENSITIVITY ---
        sens = color_menu.PARAMS["Sensitivity"]["val"]

        features = {
            "energy": (audio_features.energy_at(t) if audio_features else 0.3) * sens,
            "onset": (audio_features.onset_at(t) if audio_features else 0.0) * sens,
            "brightness": audio_features.brightness_at(t) if audio_features else 0.4,
            "percussive": (audio_features.percussive_onset_at(t) if audio_features else 0.1) * sens,
            "harmonic": audio_features.harmonic_energy_at(t) if audio_features else 0.3,
            "chroma": audio_features.chroma_at(t) if audio_features else [0.1] * 12,
            "noisiness": audio_features.noisiness_at(t) if audio_features else 0.2,
            "rolloff": audio_features.rolloff_at(t) if audio_features else 0.3
        }

        # --- BEAT-TRIGGER SYNCHRONISATION ---
        if beat_times is not None and len(beat_times) > 0 and beat_index < len(beat_times) and t >= beat_times[
            beat_index]:
            if hasattr(visualizer, 'on_beat'):
                visualizer.on_beat(strength=1.0 + features["energy"])
            if hasattr(visualizer, 'spawn_ripple'):
                visualizer.spawn_ripple(t)
            beat_index += 1

        # Onset Pulsierung
        onset_cooldown -= dt
        if onset_cooldown <= 0 and features["onset"] > (0.55 * sens):
            if hasattr(visualizer, 'micro_pulse'):
                visualizer.micro_pulse(strength=features["onset"])
            onset_cooldown = 0.05

        # Hintergrund zeichnen (Platz für Timeline lassen)
        trail_surf = pygame.Surface((width, height))
        trail_surf.set_alpha(35 if current_mode in ["flower", "stage", "grid"] else 45)
        trail_surf.fill((6, 4, 12) if current_mode in ["flower", "mandala"] else (0, 0, 0))
        screen.blit(trail_surf, (0, 0))

        # --- RENDERING (Multipliziert mit Zeitgeschwindigkeit `speed_mult`) ---
        visual_time = t * speed_mult
        try:
            if current_mode == "blobs":
                breathing = 1.0 + features["energy"] * 0.25
                speed_pulse = 0.5 + features["onset"] * 1.5
                if hasattr(visualizer, 'update'):
                    visualizer.update(dt * speed_mult)
                if hasattr(visualizer, 'draw'):
                    visualizer.draw(screen, visual_time, breathing=breathing, speed_mult=speed_pulse)
            else:
                if hasattr(visualizer, 'update_and_draw'):
                    visualizer.update_and_draw(screen, visual_time, dt * speed_mult, features)
        except Exception as rendering_error:
            print(f"[BRIDGE CRITICAL] Engine '{current_mode}' crashed. Hot-swap to Blobs! Error: {rendering_error}")
            current_mode = "blobs"
            visualizer = create_visualizer_instance(current_mode, width, height, current_colors)

        # Timeline unten einblenden
        draw_timeline(screen, t, song_length)

        # Sidebar Overlay einblenden
        if sidebar_active:
            color_menu.draw_menu(screen, current_mode, current_palette_name)

        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()