"""
Live-Overlay-Menü: Rendert die Schaltflächen direkt über die aktive Animation.
Keine eigene Schleife, blockiert den Musik- und Grafikfluss nicht!
"""
import pygame

PRESET_PALETTES = {
    "Neon Rave": [(255, 0, 150), (0, 255, 255), (150, 0, 255), (255, 255, 0)],
    "Sunset": [(255, 94, 0), (255, 0, 110), (255, 190, 11), (131, 56, 236)],
    "Ocean": [(0, 180, 216), (72, 202, 228), (0, 119, 182), (144, 224, 239)],
    "Toxic Green": [(57, 255, 20), (0, 255, 127), (173, 255, 47), (34, 139, 34)],
    "Monochrome White": [(255, 255, 255), (200, 200, 220), (150, 150, 180), (100, 100, 140)],
}

AVAILABLE_MODES = ["blobs", "stage", "grid", "mandala", "flower"]

def draw_live_overlay(screen, width, height, selected_palette_name, current_mode):
    """Zeignet das Menü als halbtransparentes Overlay über die laufende Visualisierung."""
    # 1. Hintergrund leicht abdunkeln (Alpha-Ebene)
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((10, 8, 16, 210)) # 210 von 255 Opacity -> Animation schimmert durch!
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont("arial", 24, bold=True)
    small_font = pygame.font.SysFont("arial", 16)

    palette_names = list(PRESET_PALETTES.keys())

    # --- ÜBERSCHRIFTEN ---
    title = font.render("LIVE MATRIX CONTROLLER (Press 'M' to close)", True, (0, 255, 200))
    screen.blit(title, (40, 30))

    sec1 = font.render("1. Instant Color Palette Swap", True, (255, 255, 255))
    screen.blit(sec1, (40, 75))

    # --- PALETTEN ZEICHNEN ---
    for i, name in enumerate(palette_names):
        y = 115 + i * 75
        is_sel = (name == selected_palette_name)
        box_color = (150, 50, 255) if is_sel else (70, 70, 80)
        bg_color = (35, 25, 50, 150) if is_sel else (20, 20, 30, 100)

        # Panel zeichnen
        surf = pygame.Surface((width - 80, 55), pygame.SRCALPHA)
        surf.fill(bg_color)
        screen.blit(surf, (40, y))
        pygame.draw.rect(screen, box_color, (40, y, width - 80, 55), 2, border_radius=6)

        label = small_font.render(name, True, (255, 255, 255))
        screen.blit(label, (60, y + 18))

        for j, c in enumerate(PRESET_PALETTES[name]):
            pygame.draw.circle(screen, c, (450 + j * 55, y + 27), 15)

    # --- MODI ZEICHNEN ---
    sec2 = font.render("2. Hot-Swap Visualizer Engine", True, (255, 255, 255))
    screen.blit(sec2, (40, 510))

    for i, mode_name in enumerate(AVAILABLE_MODES):
        x = 40 + i * 240
        is_sel = (mode_name == current_mode)
        btn_color = (150, 50, 255) if is_sel else (40, 35, 50)

        pygame.draw.rect(screen, btn_color, (x, 550, 220, 50), border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255) if is_sel else (80, 80, 90), (x, 550, 220, 50), 2, border_radius=6)

        txt = small_font.render(mode_name.upper(), True, (255, 255, 255))
        screen.blit(txt, (x + 110 - txt.get_width() // 2, 565))

def check_overlay_clicks(mx, my, width, height, current_palette_name, current_mode):
    """Prüft Klicks auf das Overlay und gibt geänderte Werte SOFORT zurück."""
    palette_names = list(PRESET_PALETTES.keys())

    # Paletten-Klicks
    for i, name in enumerate(palette_names):
        y_pos = 115 + i * 75
        if 40 <= mx <= width - 40 and y_pos <= my <= y_pos + 55:
            return name, current_mode

    # Modus-Klicks
    for i, mode_name in enumerate(AVAILABLE_MODES):
        x_pos = 40 + i * 240
        if x_pos <= mx <= x_pos + 220 and 550 <= my <= 600:
            return current_palette_name, mode_name

    return current_palette_name, current_mode