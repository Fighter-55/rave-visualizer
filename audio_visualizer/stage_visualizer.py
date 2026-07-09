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

        # Partikelsystem für die Strahlen
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

        # Hintergrund leicht abdunkeln für Motion Blur / Trail-Effekt
        # (Falls du ein Trail-Surface nutzt, wird das von außen gesteuert)

        # ---------------------------------------------------------
        # ZENTRALES MANDALA (Dynamische Ringe & Symmetrie)
        # ---------------------------------------------------------
        # Rotationsgeschwindigkeit hängt von Musik-Helligkeit (Centroid) ab
        self.rotation_angle += (0.5 + brightness * 2.0) * dt

        # Basis-Größe atmet mit der Energie (RMS)
        base_radius = 80 + energy * 60

        # Zeichne konzentrische, gemusterte Ringe (wie auf dem Screenshot)
        num_rings = 4
        for r in range(num_rings):
            # Ring-Radius variiert je nach Frequenz/Energie
            ring_radius = base_radius + r * 35 + (chroma[r % 12] * 20)
            # Pulsieren bei Onset
            if onset > 0.6:
                ring_radius += 15

            # Farbe wandert zyklisch durch Palette basierend auf Zeit + Ring-Index
            color = palette_gradient(self.palette, (t * 0.05) + (r * 0.15))

            # Ring zeichnen (Dicke reagiert auf Percussive-Anteil)
            thickness = max(1, int(2 + percussive * 4))
            pygame.draw.circle(surface, color, self.center, int(ring_radius), thickness)

            # Symmetrische Punkte/Blätter auf den Ringen (Mandala-Effekt)
            num_dots = 8 + r * 4
            for d in range(num_dots):
                angle = (d * (math.tau / num_dots)) + (self.rotation_angle * (1 if r % 2 == 0 else -1))
                dot_x = self.center[0] + math.cos(angle) * ring_radius
                dot_y = self.center[1] + math.sin(angle) * ring_radius

                # Punktgröße reagiert auf einzelne Chroma-Noten
                dot_size = max(2, int(3 + chroma[d % 12] * 6))
                pygame.draw.circle(surface, color, (int(dot_x), int(dot_y)), dot_size)

        # ---------------------------------------------------------
        # PARTIKEL-STRAHLEN (Schießen aus dem Zentrum)
        # ---------------------------------------------------------
        # Spawne Partikel bei starkem Onset oder kontinuierlich bei viel Energie
        if onset > 0.7 or (random.random() < 0.3 * energy):
            num_to_spawn = int(1 + onset * 4)
            for _ in range(num_to_spawn):
                p_angle = random.uniform(0, math.tau)
                p_speed = random.uniform(100, 300) + energy * 200
                p_color = palette_gradient(self.palette, random.random() + t * 0.1)
                self.particles.append({
                    "x": float(self.center[0]),
                    "y": float(self.center[1]),
                    "vx": math.cos(p_angle) * p_speed,
                    "vy": math.sin(p_angle) * p_speed,
                    "life": 1.0,
                    "color": p_color,
                    "size": random.uniform(2, 5)
                })

        # Partikel updaten und zeichnen
        alive_particles = []
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] -= dt * 1.2  # Sterbegeschwindigkeit

            if p["life"] > 0:
                # Transparenz/Alpha berechnen (Pygame benötigt dafür oft eigene Surfaces,
                # hier vereinfacht über Farb-Abschwächung für Performance)
                f = p["life"]
                c = (int(p["color"][0] * f), int(p["color"][1] * f), int(p["color"][2] * f))

                pygame.draw.circle(surface, c, (int(p["x"]), int(p["y"])), max(1, int(p["size"] * f)))
                alive_particles.append(p)
        self.particles = alive_particles

        # ---------------------------------------------------------
        # SEITLICHE FREQUENZWELLEN (Waveforms links & rechts)
        # ---------------------------------------------------------
        # Neue Amplitudenwerte in die Historie schieben
        self.wave_history_left.append(energy)
        self.wave_history_left.pop(0)
        self.wave_history_right.append(brightness)  # Rechts reagiert eher auf Höhen/Mitten
        self.wave_history_right.pop(0)

        # Parameter für das Zeichnen der Wellen
        wave_w = 150  # Breite des Wellenbereichs
        spacing_y = self.height / len(self.wave_history_left)

        for i in range(len(self.wave_history_left)):
            y_pos = int(i * spacing_y)

            # Linke Welle (Bass/Energie dominiert)
            amp_l = self.wave_history_left[i] * wave_w * (1.0 + onset * 0.5)
            color_l = palette_gradient(self.palette, (t * 0.1) + (i * 0.02))
            x_start_l = 10
            # Symmetrisches Ausschlagen von einer Mittellinie aus
            pygame.draw.line(surface, color_l, (x_start_l, y_pos), (int(x_start_l + amp_l), y_pos),
                             max(1, int(spacing_y - 2)))

            # Rechte Welle (Höhen/Mitten dominiert)
            amp_r = self.wave_history_right[i] * wave_w * (1.0 + percussive * 0.5)
            color_r = palette_gradient(self.palette, (t * 0.1) - (i * 0.02))
            x_start_r = self.width - 10
            pygame.draw.line(surface, color_r, (x_start_r, y_pos), (int(x_start_r - amp_r), y_pos),
                             max(1, int(spacing_y - 2)))

        # ---------------------------------------------------------
        # HUD / TEXT-STATISTIKEN (Untere Ecken wie im Screenshot)
        # ---------------------------------------------------------
        font = pygame.font.SysFont("monospace", 12, bold=True)
        white = (255, 255, 255)

        stats_left = [
            "AUDIO: ACTIVE",
            f"RMS ENERGY: {energy:.2f}",
            f"ONSET STRENGTH: {onset:.2f} " + ("(BEAT)" if onset > 0.6 else ""),
            f"BRIGHTNESS: {brightness:.2f}",
        ]

        stats_right = [
            f"PERC. ONSET: {percussive:.2f}",
            f"NOISINESS: {features.get('noisiness', 0.0):.2f}",
            f"ROLLOFF: {features.get('rolloff', 0.0):.2f}",
            f"CHROMA ACT.: {sum(chroma) / 12:.2f}"
        ]

        for idx, text in enumerate(stats_left):
            txt_surf = font.render(text, True, white)
            surface.blit(txt_surf, (20, self.height - 100 + idx * 18))

        for idx, text in enumerate(stats_right):
            txt_surf = font.render(text, True, white)
            surface.blit(txt_surf, (self.width - txt_surf.get_width() - 20, self.height - 100 + idx * 18))