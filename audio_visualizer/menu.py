import pygame
from audio import analyze


def run_menu():
    pygame.init()

    WIDTH, HEIGHT = 1280, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rave Visualizer Generator")

    BLACK = (0, 0, 0)
    PURPLE = (150, 50, 255)
    DARK_PURPLE = (80, 20, 160)
    WHITE = (255, 255, 255)
    GRAY = (40, 40, 40)
    LIGHT_GRAY = (100, 100, 100)

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

    # Button Abmessungen
    DROP_X, DROP_Y = int(WIDTH * 0.2), int(HEIGHT * 0.28)
    DROP_W, DROP_H = int(WIDTH * 0.6), int(HEIGHT * 0.16)

    LIVE_X, LIVE_Y = int(WIDTH * 0.35), int(HEIGHT * 0.52)
    LIVE_W, LIVE_H = int(WIDTH * 0.3), int(HEIGHT * 0.08)

    START_X, START_Y = int(WIDTH * 0.4), int(HEIGHT * 0.82)
    START_W, START_H = int(WIDTH * 0.2), int(HEIGHT * 0.08)

    MODE_X, MODE_Y = int(WIDTH * 0.1), int(HEIGHT * 0.70)
    MODE_W, MODE_H = int(WIDTH * 0.14), int(HEIGHT * 0.06)

    MODES = ["blobs", "stage", "grid", "mandala", "flower"]
    selected_mode = 0
    mode_type = "file"  # 'file' oder 'live'

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return None, None, None, None, None, None, None

            elif event.type == pygame.DROPFILE:
                filepath = event.file
                status_text = f"Loading audio file: {filepath.split('/')[-1]}"

                # Bildschirm updaten für Lade-Status
                screen.fill(BLACK)
                txt = font_medium.render("Processing audio... Please wait.", True, WHITE)
                screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))
                pygame.display.flip()

                # Audio-Analyse starten
                tempo, beat_times, audio_features = analyze(filepath)
                status_text = f"Ready! BPM: {tempo:.1f} | Beats: {len(beat_times)}"
                mode_type = "file"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Klick auf Live Input Mode
                if LIVE_X <= mx <= LIVE_X + LIVE_W and LIVE_Y <= my <= LIVE_Y + LIVE_H:
                    mode_type = "live"
                    status_text = "Live Input Mode Selected"
                    tempo = 120.0  # Dummy-Werte für den Live-Modus
                    beat_times = []
                    audio_features = None

                # Klick auf den Start Button
                elif tempo is not None and START_X <= mx <= START_X + START_W and START_Y <= my <= START_Y + START_H:
                    running = False

                # Klick auf die Visualizer-Modus Buttons
                elif MODE_Y <= my <= MODE_Y + MODE_H:
                    for i in range(len(MODES)):
                        btn_x = MODE_X + i * (MODE_W + int(WIDTH * 0.02))
                        if btn_x <= mx <= btn_x + MODE_W:
                            selected_mode = i

        # Oberfläche zeichnen
        screen.fill(BLACK)

        # Titel
        title = font_large.render("RAVE VISUALIZER", True, PURPLE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.08)))

        # Drag & Drop Zone
        pygame.draw.rect(screen, GRAY, (DROP_X, DROP_Y, DROP_W, DROP_H), border_radius=12)
        pygame.draw.rect(screen, PURPLE, (DROP_X, DROP_Y, DROP_W, DROP_H), 2, border_radius=12)

        status_render = font_small.render(status_text, True, WHITE)
        screen.blit(status_render, (WIDTH // 2 - status_render.get_width() // 2, DROP_Y + DROP_H // 2 - 12))

        # Live Input Button
        pygame.draw.rect(screen, DARK_PURPLE if mode_type != "live" else PURPLE, (LIVE_X, LIVE_Y, LIVE_W, LIVE_H),
                         border_radius=10)
        live_text = font_medium.render("LIVE INPUT MODE", True, WHITE)
        screen.blit(live_text, (WIDTH // 2 - live_text.get_width() // 2, LIVE_Y + LIVE_H // 2 - 15))

        # Visualizer Modus-Auswahl
        mode_label = font_small.render("Visual Mode Select:", True, LIGHT_GRAY)
        screen.blit(mode_label, (MODE_X, MODE_Y - 30))

        for i, mode_name in enumerate(MODES):
            btn_x = MODE_X + i * (MODE_W + int(WIDTH * 0.02))
            btn_color = PURPLE if i == selected_mode else DARK_PURPLE
            pygame.draw.rect(screen, btn_color, (btn_x, MODE_Y, MODE_W, MODE_H), border_radius=8)

            txt = font_small.render(mode_name.upper(), True, WHITE)
            screen.blit(txt, (btn_x + MODE_W // 2 - txt.get_width() // 2, MODE_Y + MODE_H // 2 - 11))

        # START Button (wird erst sichtbar, wenn eine Datei geladen oder Live gewählt ist)
        if tempo is not None or mode_type == "live":
            pygame.draw.rect(screen, PURPLE, (START_X, START_Y, START_W, START_H), border_radius=10)
            start_text = font_medium.render("START VISUALIZER", True, WHITE)
            screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, START_Y + START_H // 2 - 15))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

    # HIER IST DIE GEÄNDERTE ZEILE: Gibt exakt 7 Werte zurück (inklusive ", None" am Ende für die Farben)
    return tempo, beat_times, audio_features, filepath, mode_type, MODES[selected_mode], None