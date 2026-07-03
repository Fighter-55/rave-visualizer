import pygame
from audio import analyze

def run_menu():
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rave Visualizer Generator")

    # Colors
    BLACK = (0, 0, 0)
    PURPLE = (150, 50, 255)
    DARK_PURPLE = (80, 20, 160)
    WHITE = (255, 255, 255)
    GRAY = (40, 40, 40)
    LIGHT_GRAY = (100, 100, 100)

    # Fonts
    font_large = pygame.font.SysFont("Arial", 48, bold=True)
    font_medium = pygame.font.SysFont("Arial", 24)
    font_small = pygame.font.SysFont("Arial", 18)

    filepath = None
    tempo = None
    beat_times = None
    status_text = "Drop an audio file onto this window"

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.DROPFILE:
                filepath = event.file
                status_text = f"Analyzing: {filepath.split('/')[-1]}..."
                screen.fill(BLACK)
                pygame.display.flip()
                tempo, beat_times = analyze(filepath)
                status_text = f"Ready! Detected BPM: {tempo:.1f}"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # click-event START button
                if tempo is not None:
                    if 300 <= mouse_x <= 500 and 450 <= mouse_y <= 510:
                        return tempo, beat_times, filepath, "file"

                # click-event LIVE INPUT button
                if 250 <= mouse_x <= 550 and 360 <= mouse_y <= 420:
                    return None, None, None, "live"

        screen.fill(BLACK)

        # Title
        title = font_large.render("RAVE VISUALIZER", True, PURPLE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        subtitle = font_medium.render("GENERATOR", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 120))

        # Drop zone box
        pygame.draw.rect(screen, GRAY, (150, 200, 500, 120), border_radius=12)
        pygame.draw.rect(screen, LIGHT_GRAY, (150, 200, 500, 120), 2, border_radius=12)
        drop_text = font_small.render(status_text, True, WHITE)
        screen.blit(drop_text, (WIDTH // 2 - drop_text.get_width() // 2, 252))

        or_text = font_small.render("── or ──", True, LIGHT_GRAY)
        screen.blit(or_text, (WIDTH // 2 - or_text.get_width() // 2, 340))

        # drawing LIVE INPUT button
        pygame.draw.rect(screen, DARK_PURPLE, (250, 360, 300, 60), border_radius=10)
        live_text = font_medium.render("LIVE INPUT MODE", True, WHITE)
        screen.blit(live_text, (WIDTH // 2 - live_text.get_width() // 2, 375))

        # drawing START button
        if tempo is not None:
            pygame.draw.rect(screen, PURPLE, (300, 450, 200, 60), border_radius=10)
            start_text = font_medium.render("START", True, WHITE)
            screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 465))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return None, None, None, None