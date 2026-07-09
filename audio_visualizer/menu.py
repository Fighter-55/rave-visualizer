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

    DROP_X, DROP_Y = int(WIDTH * 0.2), int(HEIGHT * 0.3)
    DROP_W, DROP_H = int(WIDTH * 0.6), int(HEIGHT * 0.18)

    LIVE_X, LIVE_Y = int(WIDTH * 0.35), int(HEIGHT * 0.57)
    LIVE_W, LIVE_H = int(WIDTH * 0.3), int(HEIGHT * 0.09)

    START_X, START_Y = int(WIDTH * 0.38), int(HEIGHT * 0.72)
    START_W, START_H = int(WIDTH * 0.24), int(HEIGHT * 0.09)

    def draw_progress(message, step, total_steps):
        screen.fill(BLACK)
        title = font_large.render("RAVE VISUALIZER", True, PURPLE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.08)))

        msg = font_medium.render(message, True, WHITE)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, int(HEIGHT * 0.45)))

        bar_x, bar_y = int(WIDTH * 0.2), int(HEIGHT * 0.55)
        bar_w, bar_h = int(WIDTH * 0.6), 30
        pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_w, bar_h), border_radius=8)

        fill_w = int(bar_w * (step / total_steps))
        if fill_w > 0:
            pygame.draw.rect(screen, PURPLE, (bar_x, bar_y, fill_w, bar_h), border_radius=8)

        step_text = font_small.render(f"Step {step} of {total_steps}", True, LIGHT_GRAY)
        screen.blit(step_text, (WIDTH // 2 - step_text.get_width() // 2, int(HEIGHT * 0.63)))
        pygame.display.flip()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.DROPFILE:
                filepath = event.file
                tempo, beat_times, audio_features = analyze(filepath, progress_callback=draw_progress)
                status_text = f"Ready! Detected BPM: {tempo:.1f}"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                if tempo is not None:
                    if START_X <= mouse_x <= START_X + START_W and START_Y <= mouse_y <= START_Y + START_H:
                        return tempo, beat_times, audio_features, filepath, "file"

                if LIVE_X <= mouse_x <= LIVE_X + LIVE_W and LIVE_Y <= mouse_y <= LIVE_Y + LIVE_H:
                    return None, None, None, None, "live"

        screen.fill(BLACK)

        title = font_large.render("RAVE VISUALIZER", True, PURPLE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, int(HEIGHT * 0.08)))

        subtitle = font_medium.render("GENERATOR", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, int(HEIGHT * 0.2)))

        pygame.draw.rect(screen, GRAY, (DROP_X, DROP_Y, DROP_W, DROP_H), border_radius=12)
        pygame.draw.rect(screen, LIGHT_GRAY, (DROP_X, DROP_Y, DROP_W, DROP_H), 2, border_radius=12)
        drop_text = font_small.render(status_text, True, WHITE)
        screen.blit(drop_text, (WIDTH // 2 - drop_text.get_width() // 2, DROP_Y + DROP_H // 2 - 11))

        or_text = font_small.render("── or ──", True, LIGHT_GRAY)
        screen.blit(or_text, (WIDTH // 2 - or_text.get_width() // 2, int(HEIGHT * 0.52)))

        pygame.draw.rect(screen, DARK_PURPLE, (LIVE_X, LIVE_Y, LIVE_W, LIVE_H), border_radius=10)
        live_text = font_medium.render("LIVE INPUT MODE", True, WHITE)
        screen.blit(live_text, (WIDTH // 2 - live_text.get_width() // 2, LIVE_Y + LIVE_H // 2 - 15))

        if tempo is not None:
            pygame.draw.rect(screen, PURPLE, (START_X, START_Y, START_W, START_H), border_radius=10)
            start_text = font_medium.render("START", True, WHITE)
            screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, START_Y + START_H // 2 - 15))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return None, None, None, None, None