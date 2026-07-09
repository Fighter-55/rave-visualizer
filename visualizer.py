import pygame
import time
from mandala import MandalaVisualizer
from organic_blobs import BlobVisualizer
from stage_visualizer import AdvancedStageVisualizer


def run(tempo, beat_times, audio_features, filepath, mode="mandala", colors=None):
    pygame.init()

    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Rave Visualizer – {tempo:.1f} BPM [{mode.upper()}]")

    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    # Initialisierung der drei Modi
    if mode == "fluid":
        visualizer = BlobVisualizer(WIDTH, HEIGHT, palette=colors)
    elif mode == "stage":
        visualizer = AdvancedStageVisualizer(WIDTH, HEIGHT, palette=colors)
    else:
        visualizer = MandalaVisualizer(WIDTH, HEIGHT, palette=colors)

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

    # Wird für Mandala und Fluid benötigt (Motion Blur Trail)
    trail_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    running = True
    while running:
        # dt darf nicht 0 sein, mind. 0.001 fps absichern
        dt = max(0.001, clock.tick(60) / 1000.0)
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Audio-Features auslesen
        if audio_features is not None:
            features = {
                "energy": audio_features.energy_at(t),
                "onset": audio_features.onset_at(t),
                "brightness": audio_features.brightness_at(t),
                "percussive": audio_features.percussive_onset_at(t),
                "harmonic": audio_features.harmonic_energy_at(t),
                "chroma": audio_features.chroma_at(t),
                "noisiness": audio_features.noisiness_at(t),
                "rolloff": audio_features.rolloff_at(t),}