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
                if tempo is not None:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Check if START button was clicked
                    if 300 <= mouse_x <= 500 and 450 <= mouse_y <= 510:
                        return tempo, beat_times, filepath

        # Draw background
        screen.fill(BLACK)

        # Title
        title = font_large.render("AUDIO VISUALIZER", True, PURPLE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        subtitle = font_medium.render("GENERATOR", True, WHITE)
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 145))

        # Drop zone box
        pygame.draw.rect(screen, GRAY, (150, 220, 500, 120), border_radius=12)
        pygame.draw.rect(screen, LIGHT_GRAY, (150, 220, 500, 120), 2, border_radius=12)

        drop_text = font_small.render(status_text, True, WHITE)
        screen.blit(drop_text, (WIDTH // 2 - drop_text.get_width() // 2, 272))

        # START button (only visible once file is loaded)
        if tempo is not None:
            pygame.draw.rect(screen, PURPLE, (300, 450, 200, 60), border_radius=10)
            start_text = font_medium.render("START", True, WHITE)
            screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 465))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return None, None, None