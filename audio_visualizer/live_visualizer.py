import pygame
import live_audio

# Sensitivity thresholds 
BASS_THRESHOLD = 500000
MID_THRESHOLD = 200000
TREBLE_THRESHOLD = 100000

def run_live():
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rave Visualizer – Live Mode")

    # Colors
    BLACK = (0, 0, 0)
    PURPLE = (150, 50, 255)
    CYAN = (0, 255, 255)
    PINK = (255, 0, 150)

    clock = pygame.time.Clock()

    # Open microphone stream
    p, stream = live_audio.open_stream()

    # Separate pulse sizes for each band
    bass_pulse = 0
    mid_pulse = 0
    treble_pulse = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get current frequency band energies
        bass, mid, treble = live_audio.get_frequency_bands(stream)

        # Trigger pulses if energy spikes above threshold
        if bass > BASS_THRESHOLD:
            bass_pulse = 200
        if mid > MID_THRESHOLD:
            mid_pulse = 150
        if treble > TREBLE_THRESHOLD:
            treble_pulse = 100

        # Draw
        screen.fill(BLACK)

        # Bass = big purple circle
        if bass_pulse > 5:
            pygame.draw.circle(screen, PURPLE, (WIDTH // 2, HEIGHT // 2), int(bass_pulse))

        # Mid = cyan circle
        if mid_pulse > 5:
            pygame.draw.circle(screen, CYAN, (WIDTH // 2, HEIGHT // 2), int(mid_pulse))

        # Treble = small pink circle
        if treble_pulse > 5:
            pygame.draw.circle(screen, PINK, (WIDTH // 2, HEIGHT // 2), int(treble_pulse))

        # Shrink all pulses each frame
        bass_pulse *= 0.85
        mid_pulse *= 0.85
        treble_pulse *= 0.85

        pygame.display.flip()
        clock.tick(60)

    # Clean up audio stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    pygame.quit()