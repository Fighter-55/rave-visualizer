import pygame
import math
import random
from color_utils import palette_gradient


class Grid3DVisualizer:
    def __init__(self, width, height, palette):
        self.width = width
        self.height = height
        self.palette = palette

        # Fluchtpunkt exakt in der vertikalen Mitte
        self.cx = width // 2
        self.cy = height // 2

        # Gitter-Einstellungen (Exakt wie zuvor)
        self.num_rows = 20
        self.num_cols = 32
        self.grid_speed = 4.0
        self.flight_phase = 0.0

        self.history_depth = self.num_rows
        self.amplitude_history = [[0.0] * self.num_cols for _ in range(self.history_depth)]

    def update_and_draw(self, surface, t, dt, features):
        # Musik-Features extrahieren
        energy = features.get("energy", 0.2)
        onset = features.get("onset", 0.0)
        brightness = features.get("brightness", 0.4)
        percussive = features.get("percussive", 0.0)
        chroma = features.get("chroma", [0.0] * 12)

        # 1. Flug-Geschwindigkeit dynamisch anpassen
        self.grid_speed = 3.5 + energy * 7.0
        self.flight_phase += dt * self.grid_speed

        if self.flight_phase >= 1.0:
            self.flight_phase %= 1.0

            new_row = [0.0] * self.num_cols
            for c in range(self.num_cols):
                dist_from_center = abs(c - self.num_cols / 2)
                if dist_from_center > 1:
                    chroma_val = chroma[c % 12]
                    mountain_factor = math.pow(dist_from_center - 0.5, 1.3)
                    new_row[c] = (energy * 0.75 + chroma_val * 0.35) * (mountain_factor * 8)

            self.amplitude_history.insert(0, new_row)
            self.amplitude_history.pop()

        # Sanftes Beat-Wackeln für die Laser-Kreuze am Horizont
        beat_shake = (energy * 8.0) + (percussive * 6.0 if onset > 0.4 else 0.0)

        # 2. 3D-Projektion berechnen
        projected_floor = []
        projected_ceiling = []

        for r in range(self.num_rows):
            z = (r + self.flight_phase) / self.num_rows
            if z <= 0 or z > 1: continue

            floor_row = []
            ceiling_row = []

            for c in range(self.num_cols):
                x_3d = (c - self.num_cols / 2) * 70
                amp = self.amplitude_history[r][c]

                base_y_offset = 140
                y_3d_floor = base_y_offset - amp
                y_3d_ceiling = base_y_offset - amp

                if amp > 0:
                    horizon_boost = 0.6 / (z + 0.2)
                    shake = random.uniform(-beat_shake, beat_shake) * horizon_boost
                    y_3d_floor += shake
                    y_3d_ceiling += shake

                screen_x_f = self.cx + int(x_3d / z)
                screen_y_f = self.cy + int(y_3d_floor / z)
                floor_row.append((screen_x_f, screen_y_f, z))

                screen_x_c = self.cx + int(x_3d / z)
                screen_y_c = self.cy - int(y_3d_ceiling / z)
                ceiling_row.append((screen_x_c, screen_y_c, z))

            projected_floor.append(floor_row)
            projected_ceiling.append(ceiling_row)

        # 3. Gitter zeichnen (Boden & Decke)
        def draw_grid_layers(grid_data):
            for r_idx, row in enumerate(grid_data):
                z_avg = row[0][2]
                alpha_factor = max(0.0, min(1.0, 1.0 - z_avg))
                beat_glow = 0.3 * onset if onset > 0.6 else 0.0
                base_color = palette_gradient(self.palette, t * 0.04 + r_idx * 0.015 + beat_glow)

                color = (
                    max(0, min(255, int(base_color[0] * alpha_factor))),
                    max(0, min(255, int(base_color[1] * alpha_factor))),
                    max(0, min(255, int(base_color[2] * alpha_factor)))
                )
                points_2d = [(p[0], p[1]) for p in row if -100 <= p[0] <= self.width + 100]
                if len(points_2d) > 1:
                    thickness = max(1, int(3 * (1.1 - z_avg)))
                    pygame.draw.lines(surface, color, False, points_2d, thickness)

            if len(grid_data) > 1:
                for c in range(self.num_cols):
                    points_2d = []
                    z_vals = []
                    for r in range(len(grid_data)):
                        if c < len(grid_data[r]):
                            p = grid_data[r][c]
                            if -100 <= p[0] <= self.width + 100:
                                points_2d.append((p[0], p[1]))
                                z_vals.append(p[2])
                    if len(points_2d) > 1:
                        z_avg = z_vals[0]
                        alpha_factor = max(0.0, min(1.0, 1.0 - z_avg))
                        base_color = palette_gradient(self.palette, t * 0.04 + c * 0.01)
                        color = (
                            max(0, min(255, int(base_color[0] * alpha_factor))),
                            max(0, min(255, int(base_color[1] * alpha_factor))),
                            max(0, min(255, int(base_color[2] * alpha_factor)))
                        )
                        pygame.draw.lines(surface, color, False, points_2d, 2)

        draw_grid_layers(projected_floor)
        draw_grid_layers(projected_ceiling)

        # ---------------------------------------------------------
        # KORRIGIERTER, DER FLIMMERNDE & UNGLEICHMÄSSIGE MITTEL-KREIS
        # ---------------------------------------------------------
        # Basis-Größe pulsiert stabil mit der Musikenergie
        base_radius = 45 + energy * 30

        num_segments = 40
        angle_step = (2 * math.pi) / num_segments

        circle_glow = 0.4 * onset
        circle_base_color = palette_gradient(self.palette, t * 0.1 + circle_glow)

        for i in range(num_segments):
            # Ungleichmäßiges Flimmern: Schnelle Sinuswellen kombiniert mit Zufall.
            # Verhindert, dass der Kreis ganz verschwindet, sorgt aber für lebendige Lücken.
            noise_flicker = math.sin(i * 0.8 + t * 15.0) * 0.3
            visibility_chance = 0.4 + energy * 0.4 + noise_flicker

            if random.random() > max(0.1, min(0.9, visibility_chance)):
                continue

            angle1 = i * angle_step + (t * 0.4)
            angle2 = (i + 1) * angle_step + (t * 0.4)

            # DEFORMATION: Jedes Liniensegment kriegt eine leicht unregelmäßige Länge.
            # Das lässt den Kreis wellenartig zucken, anstatt perfekt rund zu sein.
            radius_wave1 = math.sin(i * 2.0 + t * 10.0) * (3.0 + brightness * 8.0)
            radius_wave2 = math.sin((i + 1) * 2.0 + t * 10.0) * (3.0 + brightness * 8.0)

            r1 = base_radius + radius_wave1
            r2 = base_radius + radius_wave2

            # Koordinaten berechnen
            x1 = self.cx + int(math.cos(angle1) * r1)
            y1 = self.cy + int(math.sin(angle1) * r1)
            x2 = self.cx + int(math.cos(angle2) * r2)
            y2 = self.cy + int(math.sin(angle2) * r2)

            # Glitchiges Shimmern für die Farbintensität
            segment_shimmer = random.uniform(0.6, 1.0)
            c_color = (
                max(0, min(255, int(circle_base_color[0] * segment_shimmer))),
                max(0, min(255, int(circle_base_color[1] * segment_shimmer))),
                max(0, min(255, int(circle_base_color[2] * segment_shimmer)))
            )

            # Stärke der Kreisfragmente wächst beim Beat an
            c_thickness = max(1, int(2 + onset * 3))

            pygame.draw.line(surface, c_color, (x1, y1), (x2, y2), c_thickness)