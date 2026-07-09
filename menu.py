import pygame
import os
from audio import analyze
from color_menu import choose_palette, PRESET_PALETTES


def run_menu():
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rave Visualizer Generator")

    BLACK = (0, 0, 0)
    PURPLE = (150, 50, 255)
    DARK_PURPLE = (80, 20, 160)
    WHITE = (255, 255, 255)
    GRAY = (40, 40, 40)
    LIGHT_GRAY = (100, 100, 100)

    # Ausfallsichere Standardschriftart für macOS/Miniforge
    font_large = pygame.font.Font(None, 54)
    font_medium = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

    filepath = None
    tempo = 120.0
    beat_times = []
    audio_features = None
    status_text = "Drop an audio file onto this window"

    menu_phase = "source"
    audio_source = "live"
    visual_mode = "mandala"
    chosen_palette_colors = PRESET_PALETTES["Neon Rave"]

    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. WICHTIG: Phasenwechsel zu 'palette' direkt hier abfangen, BEVOR Events blockieren
        if menu_phase == "palette":
            pygame.display.quit()  # Schließt das aktuelle Menüfenster
            palette_name = choose_palette(WIDTH, HEIGHT)
            chosen_palette_colors = PRESET_PALETTES.get(palette_name, PRESET_PALETTES["Neon Rave"])

            # Re-initialisiere das Hauptmenü-Fenster für die Modus-Auswahl
            pygame.init()
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("Rave Visualizer Generator")
            menu_phase = "mode"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.DROPFILE and menu_phase == "source":
                filepath = event.data
                status_text = "Analyzing audio... Please wait..."

                screen.fill(BLACK)
                lbl = font_medium.render(status_text, True, WHITE)
                screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, HEIGHT // 2))
                pygame.display.flip()

                try:
                    tempo, beat_times, audio_features = analyze(filepath)
                    audio_source = "file"
                    menu_phase = "palette"
                except Exception as e:
                    status_text = f"Error: {str(e)}"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if menu_phase == "source":
                    if WIDTH // 2 - 150 <= mx <= WIDTH // 2 + 150 and 350 <= my <= 410:
                        audio_source = "live"
                        # Setze Dummy-Werte für Live-Modus, damit der Unpacker nicht leerläuft
                        tempo = 120.0
                        beat_times = []
                        audio_features = None
                        menu_phase = "palette"

                elif menu_phase == "mode":
                    if 250 <= mx <= 550:
                        if 220 <= my <= 280:
                            visual_mode = "mandala"
                            running = False  # Beendet die Schleife sauber
                        elif 300 <= my <= 360:
                            visual_mode = "fluid"
                            running = False  # Beendet die Schleife sauber
                        elif 380 <= my <= 440:
                            visual_mode = "stage"
                            running = False  # Beendet die Schleife sauber

        #