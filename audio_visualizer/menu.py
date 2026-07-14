import pygame
import os
import threading
from audio import analyze

# Globale Variablen für Thread-Handling
analysis_progress = 0
analysis_status = "Bereit"
analysis_finished = False
analysis_result = (None, None, None)


def run_analysis_thread(filepath):
    global analysis_progress, analysis_status, analysis_finished, analysis_result
    analysis_finished = False
    analysis_progress = 0
    analysis_status = "Verbindung herstellen..."

    def callback(percent, status):
        global analysis_progress, analysis_status
        analysis_progress = percent
        analysis_status = status

    res = analyze(filepath, progress_callback=callback)
    analysis_result = res
    analysis_finished = True


def run_menu():
    global analysis_progress, analysis_status, analysis_finished, analysis_result
    pygame.init()

    WIDTH, HEIGHT = 1280, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Rave Visualizer Generator")

    # Neon Cyberpunk Palette
    BLACK = (10, 8, 16)
    PURPLE = (150, 50, 255)
    DARK_PURPLE = (60, 20, 120)
    CYAN = (0, 255, 255)
    WHITE = (255, 255, 255)
    GRAY = (30, 30, 45)
    LIGHT_GRAY = (150, 150, 170)

    font_large = pygame.font.SysFont("Arial", 64, bold=True)
    font_medium = pygame.font.SysFont("Arial", 30)
    font_small = pygame.font.SysFont("Arial", 22)

    filepath = None
    tempo = None
    beat_times = None
    audio_features = None
    status_text = "Drop an audio file onto this window"

    clock = pygame.time.Clock()
    running = True
    state = "menu"

    selected_mode = 0
    MODES = ["blobs", "stage", "grid", "mandala", "flower"]
    mode_type = "file"

    pulse_val = 0
    pulse_dir = 1

    while running:
        pulse_val += pulse_dir * 3
        if pulse_val >= 100 or pulse_val <= 0:
            pulse_dir *= -1

        WIDTH, HEIGHT = screen.get_size()

        DROP_X, DROP_Y = int(WIDTH * 0.2), int(HEIGHT * 0.28)
        DROP_W, DROP_H = int(WIDTH * 0.6), int(HEIGHT * 0.16)

        LIVE_X, LIVE_Y = int(WIDTH * 0.35), int(HEIGHT * 0.48)
        LIVE_W, LIVE_H = int(WIDTH * 0.3), int(HEIGHT * 0.08)

        MODE_X, MODE_Y = int(WIDTH * 0.15), int(HEIGHT * 0.64)
        MODE_W = int((WIDTH * 0.7) / len(MODES) - (WIDTH * 0.02))
        MODE_H = int(HEIGHT * 0.07)

        START_X, START_Y = int(WIDTH * 0.35), int(HEIGHT * 0.82)
        START_W, START_H = int(WIDTH * 0.3), int(HEIGHT * 0.09)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if state == "menu":
                if event.type == pygame.DROPFILE:
                    filepath = event.file
                    status_text = f"Selected: {os.path.basename(filepath)}"
                    mode_type = "file"

                    state = "analyzing"
                    threading.Thread(target=run_analysis_thread, args=(filepath,), daemon=True).start()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if LIVE_X <= mx <= LIVE_X + LIVE_W and LIVE_Y <= my <= LIVE_Y + LIVE_H:
                        mode_type = "live"
                        status_text = "Live Microphone Input Selected"
                        tempo, beat_times, audio_features = None, None, None

                    for i in range(len(MODES)):
                        btn_x = MODE_X + i * (MODE_W + int(WIDTH * 0.02))
                        if btn_x <= mx <= btn_x + MODE_W and MODE_Y <= my <= MODE_Y + MODE_H:
                            selected_mode = i

                    if (tempo is not None or mode_type == "live") and (
                            START_X <= mx <= START_X + START_W and START_Y <= my <= START_Y + START_H):
                        running = False

        # --- UPDATE-LOGIK FÜR DIE LAUFENDE ANALYSE (AUTOMATISCHER DIREKTSTART) ---
        if state == "analyzing":
            if analysis_finished:
                tempo, beat_times, audio_features = analysis_result
                if tempo is not None:
                    status_text = f"Successfully analyzed: {os.path.basename(filepath)} ({int(tempo)} BPM)"
                    running = False
                else:
                    status_text = "Analysis failed. Please try another file."
                    filepath = None
                    state = "menu"

        screen.fill(BLACK)

        if state == "menu":
            title = font_large.render("RAVE VISUALIZER ENGINE", True, CYAN)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.08)))

            glow_color = tuple(min(255, max(0, c + pulse_val // 2)) for c in DARK_PURPLE)
            pygame.draw.rect(screen, glow_color, (DROP_X, DROP_Y, DROP_W, DROP_H), border_radius=12)
            pygame.draw.rect(screen, CYAN if mode_type == "file" and filepath else PURPLE,
                             (DROP_X, DROP_Y, DROP_W, DROP_H), 3, border_radius=12)

            drop_lbl = font_medium.render(status_text, True, WHITE)
            screen.blit(drop_lbl, (WIDTH // 2 - drop_lbl.get_width() // 2, DROP_Y + DROP_H // 2 - 16))

            or_lbl = font_small.render("- OR -", True, LIGHT_GRAY)
            screen.blit(or_lbl, (WIDTH // 2 - or_lbl.get_width() // 2, int(HEIGHT * 0.45)))

            live_bg = PURPLE if mode_type == "live" else GRAY
            pygame.draw.rect(screen, live_bg, (LIVE_X, LIVE_Y, LIVE_W, LIVE_H), border_radius=10)
            live_border = CYAN if mode_type == "live" else LIGHT_GRAY
            pygame.draw.rect(screen, live_border, (LIVE_X, LIVE_Y, LIVE_W, LIVE_H), 2, border_radius=10)
            live_text = font_medium.render("LIVE INPUT MODE (MIC)", True, WHITE)
            screen.blit(live_text, (WIDTH // 2 - live_text.get_width() // 2, LIVE_Y + LIVE_H // 2 - 15))

            mode_label = font_small.render("Choose Visualization Engine:", True, LIGHT_GRAY)
            screen.blit(mode_label, (MODE_X, MODE_Y - 30))

            for i, mode_name in enumerate(MODES):
                btn_x = MODE_X + i * (MODE_W + int(WIDTH * 0.02))
                btn_color = PURPLE if i == selected_mode else DARK_PURPLE
                pygame.draw.rect(screen, btn_color, (btn_x, MODE_Y, MODE_W, MODE_H), border_radius=8)
                pygame.draw.rect(screen, CYAN if i == selected_mode else GRAY, (btn_x, MODE_Y, MODE_W, MODE_H), 2,
                                 border_radius=8)

                txt = font_small.render(mode_name.upper(), True, WHITE)
                screen.blit(txt, (btn_x + MODE_W // 2 - txt.get_width() // 2, MODE_Y + MODE_H // 2 - 11))

            if tempo is not None or mode_type == "live":
                start_bg = (0, min(255, 180 + pulse_val), max(0, 180 - pulse_val)) if pulse_dir == 1 else CYAN
                pygame.draw.rect(screen, PURPLE, (START_X, START_Y, START_W, START_H), border_radius=12)
                pygame.draw.rect(screen, start_bg, (START_X, START_Y, START_W, START_H), 3, border_radius=12)
                start_text = font_medium.render("LAUNCH GENERATOR", True, WHITE)
                screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, START_Y + START_H // 2 - 15))

        elif state == "analyzing":
            analyzing_title = font_large.render("EXTRACTING AUDIO FEATURES", True, PURPLE)
            screen.blit(analyzing_title, (WIDTH // 2 - analyzing_title.get_width() // 2, int(HEIGHT * 0.25)))

            status_lbl = font_medium.render(analysis_status, True, WHITE)
            screen.blit(status_lbl, (WIDTH // 2 - status_lbl.get_width() // 2, int(HEIGHT * 0.42)))

            bar_x, bar_y = int(WIDTH * 0.2), int(HEIGHT * 0.52)
            bar_w, bar_h = int(WIDTH * 0.6), 40

            pygame.draw.rect(screen, (20, 20, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=10)
            pygame.draw.rect(screen, DARK_PURPLE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)

            fill_w = int(bar_w * (analysis_progress / 100.0))
            if fill_w > 0:
                pygame.draw.rect(screen, CYAN, (bar_x + 4, bar_y + 4, fill_w - 8, bar_h - 8), border_radius=7)
                glow_alpha = 100 + pulse_val
                highlight_surf = pygame.Surface((fill_w - 8, bar_h - 8), pygame.SRCALPHA)
                highlight_surf.fill((255, 255, 255, int(glow_alpha * 0.25)))
                screen.blit(highlight_surf, (bar_x + 4, bar_y + 4))

            pct_text = font_medium.render(f"{analysis_progress}%", True, CYAN)
            screen.blit(pct_text, (WIDTH // 2 - pct_text.get_width() // 2, bar_y + 55))

            hint_text = font_small.render("Please keep the window active. Audio mathematics are intensive...", True,
                                          LIGHT_GRAY)
            screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, int(HEIGHT * 0.75)))

        pygame.display.flip()
        clock.tick(60)

    return tempo, beat_times, audio_features, filepath, mode_type, MODES[selected_mode], None