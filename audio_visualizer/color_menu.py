"""
Live-Overlay-Menü mit interaktivem Farbrad (Color Wheel),
Parameter-Slidern für Live-Echtzeit-Steuerung und Triebwerksauswahl.
"""
import pygame
import math
import colorsys

# Standard-Presets
PRESET_PALETTES = {
    "Neon Rave": [(255, 0, 150), (0, 255, 255), (150, 0, 255), (255, 255, 0)],
    "Sunset": [(255, 94, 0), (255, 0, 110), (255, 190, 11), (131, 56, 236)],
    "Ocean": [(0, 180, 216), (72, 202, 228), (0, 119, 182), (144, 224, 239)],
    "Toxic Green": [(57, 255, 20), (0, 255, 127), (173, 255, 47), (34, 139, 34)],
    "Monochrome White": [(255, 255, 255), (200, 200, 220), (150, 150, 180), (100, 100, 140)],
}

AVAILABLE_MODES = ["blobs", "stage", "grid", "mandala", "flower"]

# Globale Live-Parameter (Wert, Min, Max, Anzeigename)
PARAMS = {
    "Sensitivity": {"val": 1.0, "min": 0.5, "max": 2.5, "label": "Music Sensitivity"},
    "Speed": {"val": 1.0, "min": 0.2, "max": 3.0, "label": "Animation Speed"},
    "Symmetry": {"val": 8.0, "min": 4.0, "max": 24.0, "label": "Symmetry Axes"},
}

# Globale Variablen für das Custom-Farbsystem
CUSTOM_COLORS = [(255, 0, 150), (0, 255, 255), (150, 0, 255), (255, 255, 0)]
ACTIVE_SLOT = 0

# Layout-Konstanten
SIDEBAR_WIDTH = 750
WHEEL_RADIUS = 100
WHEEL_SURFACE = None

def get_wheel_center(screen_width):
    return (screen_width - SIDEBAR_WIDTH + 570, 260)

def get_color_from_wheel(mx, my, screen_width):
    cx, cy = get_wheel_center(screen_width)
    dx = mx - cx
    dy = my - cy
    distance = math.hypot(dx, dy)

    if distance > WHEEL_RADIUS:
        return None

    angle = math.atan2(dy, dx)
    hue = (angle + math.pi) / (2 * math.pi)
    saturation = distance / WHEEL_RADIUS
    value = 1.0

    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return (int(r * 255), int(g * 255), int(b * 255))

def draw_color_wheel(screen, cx, cy):
    global WHEEL_SURFACE
    size = WHEEL_RADIUS * 2

    if WHEEL_SURFACE is None:
        WHEEL_SURFACE = pygame.Surface((size, size), pygame.SRCALPHA)
        for y in range(size):
            for x in range(size):
                dx = x - WHEEL_RADIUS
                dy = y - WHEEL_RADIUS
                dist = math.hypot(dx, dy)

                if dist <= WHEEL_RADIUS:
                    angle = math.atan2(dy, dx)
                    hue = (angle + math.pi) / (2 * math.pi)
                    sat = dist / WHEEL_RADIUS
                    r, g, b = colorsys.hsv_to_rgb(hue, sat, 1.0)
                    WHEEL_SURFACE.set_at((x, y), (int(r*255), int(g*255), int(b*255), 255))

    screen.blit(WHEEL_SURFACE, (cx - WHEEL_RADIUS, cy - WHEEL_RADIUS))
    pygame.draw.circle(screen, (80, 80, 95), (cx, cy), WHEEL_RADIUS, 2)

def draw_menu(screen, current_mode, current_palette_name):
    width, height = screen.get_size()
    cx, cy = get_wheel_center(width)

    # Hintergrund-Glas
    menu_surf = pygame.Surface((SIDEBAR_WIDTH, height), pygame.SRCALPHA)
    menu_surf.fill((10, 8, 22, 240))
    screen.blit(menu_surf, (width - SIDEBAR_WIDTH, 0))

    # Trennlinie
    pygame.draw.line(screen, (130, 60, 255), (width - SIDEBAR_WIDTH, 0), (width - SIDEBAR_WIDTH, height), 3)

    font_title = pygame.font.SysFont("Arial", 28, bold=True)
    font_sec = pygame.font.SysFont("Arial", 21, bold=True)
    font_small = pygame.font.SysFont("Arial", 16)

    # --- TITEL ---
    title_text = font_title.render("VISUALIZER CONTROL CENTER", True, (255, 255, 255))
    screen.blit(title_text, (width - SIDEBAR_WIDTH + 40, 40))

    # --- SEKTION 1: PRESETS (LINKS) ---
    sec1 = font_sec.render("1. Standard Presets", True, (0, 255, 255))
    screen.blit(sec1, (width - SIDEBAR_WIDTH + 40, 100))

    y_offset = 140
    for name, colors in PRESET_PALETTES.items():
        is_active = (name == current_palette_name)
        text_color = (0, 255, 255) if is_active else (210, 210, 210)

        label = font_small.render(name, True, text_color)
        screen.blit(label, (width - SIDEBAR_WIDTH + 50, y_offset + 6))

        for j, c in enumerate(colors):
            pygame.draw.circle(screen, c, (width - SIDEBAR_WIDTH + 240 + j * 35, y_offset + 14), 11)

        if is_active:
            pygame.draw.rect(screen, (0, 255, 255), (width - SIDEBAR_WIDTH + 35, y_offset, 345, 30), 1, border_radius=4)

        y_offset += 38

    # --- SEKTION 2: PALETTE DESIGNER (RECHTS) ---
    sec_custom = font_sec.render("2. Palette Designer", True, (255, 0, 150))
    screen.blit(sec_custom, (width - SIDEBAR_WIDTH + 420, 100))

    draw_color_wheel(screen, cx, cy)

    # Slots
    slot_y = 380
    for i in range(4):
        slot_x = width - SIDEBAR_WIDTH + 420 + (i * 72)
        is_active = (i == ACTIVE_SLOT)
        border_color = (255, 255, 255) if is_active else (70, 70, 85)
        border_width = 3 if is_active else 1

        pygame.draw.rect(screen, CUSTOM_COLORS[i], (slot_x, slot_y, 58, 34), border_radius=5)
        pygame.draw.rect(screen, border_color, (slot_x, slot_y, 58, 34), border_width, border_radius=5)

        num_text = font_small.render(f"Slot {i+1}", True, (255, 255, 255) if is_active else (160, 160, 170))
        screen.blit(num_text, (slot_x + 8, slot_y + 38))

    # Apply Button
    btn_x = width - SIDEBAR_WIDTH + 420
    btn_y = 455
    btn_color = (255, 0, 150) if current_palette_name == "Custom" else (35, 30, 45)
    pygame.draw.rect(screen, btn_color, (btn_x, btn_y, 274, 35), border_radius=6)
    pygame.draw.rect(screen, (255, 255, 255), (btn_x, btn_y, 274, 35), 1, border_radius=6)
    btn_txt = font_small.render("APPLY CUSTOM PALETTE", True, (255, 255, 255))
    screen.blit(btn_txt, (btn_x + 137 - btn_txt.get_width() // 2, btn_y + 8))

    # --- SEKTION 3: LIVE PARAMETER SLIDER (LINKS UNTEN) ---
    sec_sliders = font_sec.render("3. Live Engine Controls", True, (0, 255, 255))
    screen.blit(sec_sliders, (width - SIDEBAR_WIDTH + 40, 345))

    slider_y = 385
    for key, data in PARAMS.items():
        # Label & Wert anzeigen
        txt_label = font_small.render(f"{data['label']}: {data['val']:.2f}", True, (230, 230, 230))
        screen.blit(txt_label, (width - SIDEBAR_WIDTH + 50, slider_y))

        # Slider Bahn zeichnen
        track_x = width - SIDEBAR_WIDTH + 50
        track_w = 280
        pygame.draw.line(screen, (60, 60, 75), (track_x, slider_y + 24), (track_x + track_w, slider_y + 24), 6)

        # Slider Kopf Position berechnen
        frac = (data["val"] - data["min"]) / (data["max"] - data["min"])
        head_x = track_x + int(frac * track_w)

        # Kopf zeichnen
        pygame.draw.circle(screen, (0, 255, 255), (head_x, slider_y + 24), 8)
        slider_y += 50

    # --- SEKTION 4: ENGINES (GANZ UNTEN) ---
    sec4 = font_sec.render("4. Hot-Swap Visualizer Engine", True, (255, 255, 255))
    screen.blit(sec4, (width - SIDEBAR_WIDTH + 40, 545))

    for i, mode_name in enumerate(AVAILABLE_MODES):
        x = width - SIDEBAR_WIDTH + 40 + i * 136
        is_sel = (mode_name == current_mode)
        btn_color = (130, 60, 255) if is_sel else (35, 30, 45)

        pygame.draw.rect(screen, btn_color, (x, 585, 126, 45), border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255) if is_sel else (70, 70, 85), (x, 585, 126, 45), 1 if not is_sel else 2, border_radius=6)

        txt = font_small.render(mode_name.upper(), True, (255, 255, 255))
        screen.blit(txt, (x + 63 - txt.get_width() // 2, 597))


def handle_menu_events(event, current_mode, current_palette_name, screen_width):
    global ACTIVE_SLOT, CUSTOM_COLORS, PARAMS

    if event.type != pygame.MOUSEBUTTONDOWN:
        return None, None

    mx, my = event.pos
    menu_left_x = screen_width - SIDEBAR_WIDTH

    if mx < menu_left_x:
        return None, None

    # --- 1. PRESETS ---
    y_offset = 140
    for name in PRESET_PALETTES.keys():
        if menu_left_x + 35 <= mx <= menu_left_x + 380 and y_offset <= my <= y_offset + 30:
            return None, name
        y_offset += 38

    # --- 2. CUSTOM SLOTS ---
    slot_y = 380
    for i in range(4):
        slot_x = screen_width - SIDEBAR_WIDTH + 420 + (i * 72)
        if slot_x <= mx <= slot_x + 58 and slot_y <= my <= slot_y + 34:
            ACTIVE_SLOT = i
            return None, None

    # --- 3. FARBRAD ---
    picked_color = get_color_from_wheel(mx, my, screen_width)
    if picked_color is not None:
        CUSTOM_COLORS[ACTIVE_SLOT] = picked_color
        if current_palette_name == "Custom":
            PRESET_PALETTES["Custom"] = list(CUSTOM_COLORS)
            return None, "Custom"
        return None, None

    # --- 4. APPLY BUTTON ---
    btn_x = screen_width - SIDEBAR_WIDTH + 420
    btn_y = 455
    if btn_x <= mx <= btn_x + 274 and btn_y <= my <= btn_y + 35:
        PRESET_PALETTES["Custom"] = list(CUSTOM_COLORS)
        return None, "Custom"

    # --- 5. SLIDERS KLICKBARER BEREICH (Snapping) ---
    slider_y = 385
    for key, data in PARAMS.items():
        track_x = screen_width - SIDEBAR_WIDTH + 50
        track_w = 280
        # Toleranzbereich um die Slider-Achse abfragen
        if track_x <= mx <= track_x + track_w and slider_y + 10 <= my <= slider_y + 38:
            frac = (mx - track_x) / track_w
            new_val = data["min"] + frac * (data["max"] - data["min"])
            data["val"] = max(data["min"], min(data["max"], new_val))
            # Gibt ein Signal zurück, dass die Parameter aktualisiert wurden
            return "PARAMS_UPDATED", None
        slider_y += 50

    # --- 6. ENGINES ---
    for i, mode_name in enumerate(AVAILABLE_MODES):
        x = screen_width - SIDEBAR_WIDTH + 40 + i * 136
        if x <= mx <= x + 126 and 585 <= my <= 585 + 45:
            return mode_name, None

    return None, None