"""
Kleines Vor-Menü: Nutzer wählt eine Farbpalette für die Visualisierung aus.
Wird spaeter fuer alle Visualisierungs-Optionen wiederverwendet.
"""

import pygame

PRESET_PALETTES = {
    "Neon Rave": [(255, 0, 150), (0, 255, 255), (150, 0, 255), (255, 255, 0)],
    "Sunset": [(255, 94, 0), (255, 0, 110), (255, 190, 11), (131, 56, 236)],
    "Ocean": [(0, 180, 216), (72, 202, 228), (0, 119, 182), (144, 224, 239)],
    "Toxic Green": [(57, 255, 20), (0, 255, 127), (173, 255, 47), (34, 139, 34)],
    "Monochrome White": [(255, 255, 255), (200, 200, 220), (150, 150, 180), (100, 100, 140)],
}


def choose_palette(width=900, height=650):
    """Zeigt ein einfaches Auswahlmenü und gibt die gewaehlte Palette
    (Liste von (r,g,b) Tupeln) zurueck."""
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Choose a Color Palette")
    font = pygame.font.SysFont("arial", 26)
    small_font = pygame.font.SysFont("arial", 18)
    clock = pygame.time.Clock()

    names = list(PRESET_PALETTES.keys())
    selected = 0
    confirmed_name = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                confirmed_name = names[0]
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(names)
                elif event.key == pygame.K_UP:
                    selected = (selected - 1) % len(names)
                elif event.key == pygame.K_RETURN:
                    confirmed_name = names[selected]
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                idx = (my - 100) // 90
                if 0 <= idx < len(names) and 100 <= my:
                    confirmed_name = names[idx]
                    running = False

        screen.fill((15, 15, 20))
        title = font.render("Chose with arrowkeys", True, (255, 255, 255))
        screen.blit(title, (30, 30))

        for i, name in enumerate(names):
            y = 100 + i * 90
            box_color = (255, 255, 255) if i == selected else (70, 70, 70)
            pygame.draw.rect(screen, box_color, (40, y, width - 80, 70), 2, border_radius=10)
            label = small_font.render(name, True, (255, 255, 255))
            screen.blit(label, (60, y + 25))
            for j, c in enumerate(PRESET_PALETTES[name]):
                pygame.draw.circle(screen, c, (420 + j * 55, y + 35), 20)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return PRESET_PALETTES[confirmed_name]
