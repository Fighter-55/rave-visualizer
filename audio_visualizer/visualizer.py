import pygame
import time
from mandala import MandalaVisualizer
from organic_blobs import BlobVisualizer
from stage_visualizer import AdvancedStageVisualizer
from color_menu import PRESET_PALETTES

PANEL_WIDTH = 320

def run(tempo, beat_times, filepath, mode="mandala", colors=None, audio_features=None, width=1280, height=800):
    pygame.init()

    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(f"Rave Visualizer – {tempo:.1f} BPM [{mode.upper()}]")

    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    # Colors
    BLACK = (0, 0, 0)
    PURPLE = (150, 50, 255)
    DARK_PURPLE = (80, 20, 160)
    WHITE = (255, 255, 255)
    GRAY = (40, 40, 40)
    LIGHT_GRAY = (100, 100, 100)

    font_medium = pygame.font.SysFont("Arial", 22, bold=True)
    font_small = pygame.font.SysFont("Arial", 16)

    def create_visualizer(m, c):
        if m == "blobs":
            return BlobVisualizer(width, height, palette=c)
        elif m == "stage":
            return AdvancedStageVisualizer(width, height, palette=c)
        else:
            return MandalaVisualizer(width, height, palette=c)

    current_mode = mode
    current_colors = colors
    visualizer = create_visualizer(current_mode, current_colors)

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
    panel_open = False
    MODES = ["mandala", "blobs", "stage"]
    PALETTE_NAMES = list(PRESET_PALETTES.keys())

    running = True
    while running:
        dt = max(0.001, clock.tick(60) / 1000.0)
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_m:
                    panel_open = not panel_open

            if event.type == pygame.MOUSEBUTTONDOWN and panel_open:
                mx, my = pygame.mouse.get_pos()
                panel_x = width - PANEL_WIDTH

                # Mode buttons
                for i, m in enumerate(MODES):
                    btn_y = 100 + i * 60
                    if panel_x + 20 <= mx <= panel_x + PANEL_WIDTH - 20 and btn_y <= my <= btn_y + 44:
                        current_mode = m
                        visualizer = create_visualizer(current_mode, current_colors)
                        beat_index = 0

                # Palette buttons
                for i, name in enumerate(PALETTE_NAMES):
                    btn_y = 320 + i * 55
                    if panel_x + 20 <= mx <= panel_x + PANEL_WIDTH - 20 and btn_y <= my <= btn_y + 40:
                        current_colors = PRESET_PALETTES[name]
                        visualizer = create_visualizer(current_mode, current_colors)

        if audio_features is not None:
            features = {
                "energy":     audio_features.energy_at(t),
                "onset":      audio_features.onset_at(t),
                "brightness": audio_features.brightness_at(t),
                "percussive": audio_features.percussive_onset_at(t),
                "harmonic":   audio_features.harmonic_energy_at(t),
                "chroma":     audio_features.chroma_at(t),
                "noisiness":  audio_features.noisiness_at(t),
                "rolloff":    audio_features.rolloff_at(t),
            }
        else:
            features = {
                "energy": 0.4, "onset": 0.0, "brightness": 0.4,
                "percussive": 0.0, "harmonic": 0.3,
                "chroma": [0.0] * 12, "noisiness": 0.2, "rolloff": 0.3,
            }

        # Beat detection
        if beat_index < len(beat_times) and t >= beat_times[beat_index]:
            if current_mode == "mandala":
                visualizer.spawn_ripple(t)
            elif current_mode == "blobs":
                visualizer.on_beat(strength=1.0 + features["energy"])
            beat_index += 1

        if current_mode == "blobs":
            onset_cooldown -= dt
            if onset_cooldown <= 0 and features["onset"] > 0.55:
                visualizer.micro_pulse(strength=features["onset"] * 0.6)
                onset_cooldown = 0.06

        if current_mode == "mandala":
            visualizer.maybe_spawn_sparks(t, max(features["rolloff"], features["noisiness"]))

        # Draw visualizer
        if current_mode == "blobs":
            breathing = 1.0 + features["energy"] * 0.22
            speed_mult = 0.6 + features["brightness"] * 1.4
            fade = pygame.Surface((width, height))
            fade.set_alpha(45)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
            visualizer.update(dt)
            visualizer.draw(screen, t, breathing=breathing, speed_mult=speed_mult)
        elif current_mode == "stage":
            fade = pygame.Surface((width, height))
            fade.set_alpha(40)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
            visualizer.update_and_draw(screen, t, dt, features)
        else:
            screen.fill((6, 4, 12))
            visualizer.draw(screen, t, dt, features)

        # Draw side panel
        if panel_open:
            panel_x = width - PANEL_WIDTH
            panel_surf = pygame.Surface((PANEL_WIDTH, height), pygame.SRCALPHA)
            panel_surf.fill((10, 10, 20, 210))
            screen.blit(panel_surf, (panel_x, 0))

            # Panel title
            title = font_medium.render("SETTINGS  [M]", True, WHITE)
            screen.blit(title, (panel_x + 20, 30))

            pygame.draw.line(screen, LIGHT_GRAY, (panel_x + 20, 70), (width - 20, 70), 1)

            # Mode buttons
            mode_label = font_small.render("VISUAL MODE", True, LIGHT_GRAY)
            screen.blit(mode_label, (panel_x + 20, 78))

            for i, m in enumerate(MODES):
                btn_y = 100 + i * 60
                btn_color = PURPLE if m == current_mode else DARK_PURPLE
                pygame.draw.rect(screen, btn_color, (panel_x + 20, btn_y, PANEL_WIDTH - 40, 44), border_radius=8)
                label = font_medium.render(m.upper(), True, WHITE)
                screen.blit(label, (panel_x + 20 + (PANEL_WIDTH - 40) // 2 - label.get_width() // 2, btn_y + 12))

            pygame.draw.line(screen, LIGHT_GRAY, (panel_x + 20, 295), (width - 20, 295), 1)

            # Palette buttons
            palette_label = font_small.render("COLOR PALETTE", True, LIGHT_GRAY)
            screen.blit(palette_label, (panel_x + 20, 305))

            for i, name in enumerate(PALETTE_NAMES):
                btn_y = 320 + i * 55
                is_selected = PRESET_PALETTES[name] == current_colors
                border_color = WHITE if is_selected else GRAY
                pygame.draw.rect(screen, (20, 20, 30), (panel_x + 20, btn_y, PANEL_WIDTH - 40, 40), border_radius=6)
                pygame.draw.rect(screen, border_color, (panel_x + 20, btn_y, PANEL_WIDTH - 40, 40), 2, border_radius=6)
                name_label = font_small.render(name, True, WHITE)
                screen.blit(name_label, (panel_x + 25, btn_y + 12))
                # Color dots
                for j, c in enumerate(PRESET_PALETTES[name]):
                    pygame.draw.circle(screen, c, (panel_x + PANEL_WIDTH - 30 - j * 22, btn_y + 20), 8)

            # Hint at bottom
            hint = font_small.render("F = fullscreen  ESC = quit", True, LIGHT_GRAY)
            screen.blit(hint, (panel_x + 20, height - 30))

        pygame.display.flip()

    pygame.quit()