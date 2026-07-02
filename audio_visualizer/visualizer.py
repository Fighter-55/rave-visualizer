import pygame
import time

def run(tempo, beat_times, filepath):
    pygame.init()

    pygame.mixer.init()
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Rave Visualizer – {tempo:.1f} BPM")

    BLACK = (0, 0, 0)
    PURPLE = (150, 50, 255)

    clock = pygame.time.Clock()
    start_time = time.time()

    beat_index = 0
    pulse_size = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time() - start_time

        if beat_index < len(beat_times):
            if current_time >= beat_times[beat_index]:
                if pulse_size < 50:
                    pulse_size = 200
                beat_index += 1

        screen.fill(BLACK)
        if pulse_size > 10:
            pygame.draw.circle(screen, PURPLE, (WIDTH // 2, HEIGHT // 2), int(pulse_size))
        pulse_size *= 0.9

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()