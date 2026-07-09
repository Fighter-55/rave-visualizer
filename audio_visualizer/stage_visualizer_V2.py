import pygame
import math
import random
from color_utils import palette_gradient


class AdvancedStageVisualizer:
    def __init__(self, width, height, palette):
        self.width = width
        self.height = height
        self.palette = palette
        self.center = (width // 2, height // 2)

        # Partikelsystem für die Strahlen (Feuerwerk)
        self.particles = []
        # Rotation des Mandalas
        self.rotation_angle = 0.0
        # Puffer für die Wellenformen (historische Amplituden für flüssige Bewegung)
        self.wave_history_left = [0.0] * 40
        self.wave_history_right = [0.0] * 40

    def update_and_draw(self, surface, t, dt, features):
        """
        features ist ein normiertes Dict (0.0 bis 1.0):
        - energy (RMS)
        - onset (Ausschlag)
        - brightness (Centroid)
        - percussive (Snare/Kick)
        - harmonic (Melodie)
        - chroma (Liste von 12 Notenwerten)
        """
        # 1. Parameter extrahieren mit Fallbacks
        energy = features.get("energy", 0.2)
        onset = features.get("onset", 0.0)
        brightness = features.get("brightness", 0.4)
        percussive = features.get("percussive", 0.0)
        chroma = features.get("chroma", [0.0] * 12)

        # ---------------------------------------------------------
        # ZENTRALES MANDALA (Ringe mit mehr Abstand)
        # ---------------------------------------------------------
        # Rotationsgeschwindigkeit hängt von Musik-Helligkeit ab
        self.rotation_angle += (0.4 + brightness * 2.2) * dt

        # Basis-Größe atmet mit der Energie
        base_radius = 70 + energy * 50

        # Zeichne konzentrische Ringe (Abstand von 35 auf 55 erhöht für mehr Weite)
        num_rings = 4
        for r in range(num_rings):
            # Größerer Abstand zwischen den Ringen
            ring_radius = base_radius + r * 55 + (chroma[r % 12] * 25)

            # Pulsieren bei Onset
            if onset > 0.6:
                ring_radius += 20

            # Farbe wandert zyklisch durch Palette basierend auf Zeit + Ring-Index
            color = palette_gradient(self.palette, (t * 0.05) + (r * 0.12))

            # Ring zeichnen
            thickness = max(1, int(1 + percussive * 3))
            pygame.draw.circle(surface, color, self.center, int(ring_radius), thickness)

            # Symmetrische Punkte auf den Ringen
            num_dots = 8 + r * 4
            for d in range(num_dots):
                angle = (d * (math.tau / num_dots)) + (self.rotation_angle * (1 if r % 2 == 0 else -1))
                dot_x = self.center[0] + math.cos(angle) * ring_radius
                dot_y = self.center[1] + math.sin(angle) * ring_radius

                # Punktgröße reagiert auf einzelne Chroma-Noten
                dot_size = max(2, int(2 + chroma[d % 12] * 5))
                pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_size)

        # ---------------------------------------------------------
        # FEUERWERK-EFFEKT (Partikel-Strahlen aus dem Zentrum)
        # ---------------------------------------------------------
        # Mehr Partikel bei starkem Onset, höhere Grundgeschwindigkeit
        if onset > 0.6 or (random.random() < 0.4 * energy):
            # Erhöhte Anzahl an Partikeln für fetteren Effekt
            num_to_spawn = int(2 + onset * 8)
            for _ in range(num_to_spawn):
                p_angle = random.uniform(0, math.tau)
                # Höhere Geschwindigkeit (von 100-300 auf 150-450 erhöht)
                p_speed = random.uniform(150, 450) + energy * 250
                p_color = palette_gradient(self.palette, random.random() + t * 0.08)
                self.particles.append({
                    "x": float(self.center[0]),
                    "y": float(self.center[1]),
                    "vx": math.cos(p_angle) * p_speed,
                    "vy": math.sin(p_angle) * p_speed,
                    "life": random.uniform(0.8, 1.4),  # Etwas längere Lebensdauer
                    "color": p_color,
                    "size": random.uniform(2.5, 6.0)  # Leicht vergrößert für bessere Sichtbarkeit
                })

        # Partikel updaten und zeichnen
        alive_particles = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt * 1.0  # Sanfterer Kometenschweif-Effekt

            if p["life"] > 0:
                f = p["life"]
                # Farb-Fadeout im Flug
                c = (int(p["color"][0] * f), int(p["color"][1] * f), int(p["color"][2] * f))

                # --- DAS HIER VOR ZEILE 110 EINFÜGEN ---
                # Wir stellen sicher, dass jeder RGB-Wert zwingend zwischen 0 und 255 liegt
                if isinstance(c, (list, tuple)) and len(c) >= 3:
                    r = max(0, min(255, int(c[0])))
                    g = max(0, min(255, int(c[1])))
                    b = max(0, min(255, int(c[2])))
                    c = (r, g, b)
                else:
                    c = (255, 255, 255)  # Notfall-Farbe Weiß, falls 'c' komplett kaputt ist
                # --------------------------------------

                # Das ist eure originale Zeile 110:
                pygame.draw.circle(surface, c, (int(p["x"]), int(p["y"])), max(1, int(p["size"] * f)))
        # ---------------------------------------------------------
        # SEITLICHE FREQUENZWELLEN (Schmalere Balken am Rand)
        # ---------------------------------------------------------
        self.wave_history_left.append(energy)
        self.wave_history_left.pop(0)
        self.wave_history_right.append(brightness)
        self.wave_history_right.pop(0)

        wave_w = 120  # Breite der Wellen etwas kompakter gehalten
        spacing_y = self.height / len(self.wave_history_left)

        for i in range(len(self.wave_history_left)):
            y_pos = int(i * spacing_y)

            # Linke feine Welle
            amp_l = self.wave_history_left[i] * wave_w * (1.0 + onset * 0.4)
            color_l = palette_gradient(self.palette, (t * 0.1) + (i * 0.02))
            x_start_l = 10
            # Breite starr auf feine Linien limitiert (max 1-2 Pixel dick)
            pygame.draw.line(surface, color_l, (x_start_l, y_pos), (int(x_start_l + amp_l), y_pos), 1)

            # Rechte feine Welle
            amp_r = self.wave_history_right[i] * wave_w * (1.0 + percussive * 0.4)
            color_r = palette_gradient(self.palette, (t * 0.1) - (i * 0.02))
            x_start_r = self.width - 10
            pygame.draw.line(surface, color_r, (x_start_r, y_pos), (int(x_start_r - amp_r), y_pos), 1)

        # Die HUD/Text-Sektion wurde komplett gelöscht.