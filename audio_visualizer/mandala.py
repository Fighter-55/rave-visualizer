"""
Option 2: Mandala-Visualisierung.
Von einem zentralen Punkt aus entstehen symmetrisch angeordnete Formen -
Strahlen, Ringe, Blaetter, ein Farbrad, Funken. Jedes Element ist an ein
eigenes librosa-Feature gekoppelt und wird NUR sichtbar, wenn dieses
Feature gerade aktiv ist (mit weichem Ein-/Ausblenden). Bei energiereichen
Song-Passagen sind entsprechend many Elemente gleichzeitig aktiv.
"""

import pygame
import math
import random
import time

from color_utils import palette_gradient


def smoothstep(value, edge0, edge1):
    """Weicher 0..1 Uebergang zwischen edge0 und edge1 (kein hartes Ein/Aus)."""
    if edge1 <= edge0:
        return 0.0
    x = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return x * x * (3 - 2 * x)


class Ripple:
    """Vom Beat ausgeloeste, nach aussen wandernde Ringwelle."""
    def __init__(self, birth_t, color):
        self.birth_t = birth_t
        self.color = color

    def draw(self, surface, center, t, max_radius, life=1.4):
        try:
            f = (t - self.birth_t) / life
            if f >= 1.0:
                return False
            radius = f * max_radius * 1.15
            alpha = int(180 * (1 - f))
            if radius > 1 and alpha > 2:
                pygame.draw.circle(surface, (*self.color, alpha), center, int(radius), width=4)
        except Exception:
            pass
        return True


class Spark:
    """Kurzlebiger Funke im aeusseren Bereich (Treble/Sparkle-Layer)."""
    def __init__(self, birth_t, angle, radius, color):
        self.birth_t = birth_t
        self.angle = angle
        self.radius = radius
        self.color = color

    def draw(self, surface, center, t, life=0.5):
        try:
            f = (t - self.birth_t) / life
            if f >= 1.0:
                return False
            size = max(2, int(6 * (1 - f)))
            alpha = int(255 * (1 - f))
            x = center[0] + math.cos(self.angle) * self.radius
            y = center[1] + math.sin(self.angle) * self.radius
            pygame.draw.circle(surface, (*self.color, alpha), (int(x), int(y)), size)
        except Exception:
            pass
        return True


class MandalaVisualizer:
    def __init__(self, width, height, palette, symmetry=10):
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        self.max_radius = min(width, height) * 0.55
        self.palette = palette
        self.symmetry = symmetry

        self.ripples = []
        self.sparks = []
        self.rotation_rays = 0.0
        self.rotation_petals = 0.0

    # ---- Layer 1: zentraler Kern -> RMS-Energie, immer sichtbar ----
    def draw_core(self, surface, t, energy):
        try:
            radius = 28 + energy * 75
            for scale, alpha_mult in ((1.8, 0.15), (1.3, 0.3), (1.0, 0.9)):
                color = palette_gradient(self.palette, t * 0.05)
                alpha = int(255 * alpha_mult)
                pygame.draw.circle(surface, (*color, alpha), self.center, int(radius * scale))
        except Exception:
            pass

    # ---- Layer 2: Beat-Ringe -> beat_times (Event-basiert) ----
    def spawn_ripple(self, t):
        color = palette_gradient(self.palette, t * 0.05 + 0.3)
        self.ripples.append(Ripple(t, color))

    def draw_ripples(self, surface, t):
        self.ripples = [r for r in self.ripples if r.draw(surface, self.center, t, self.max_radius)]

    # ---- Layer 3: perkussive Strahlen -> percussive_onset ----
    def draw_rays(self, surface, t, activity, dt):
        try:
            visible = smoothstep(activity, 0.22, 0.57)
            if visible <= 0.01:
                return
            self.rotation_rays += dt * (0.15 + activity * 0.6)
            length = self.max_radius * (0.45 + activity * 0.65)
            for i in range(self.symmetry):
                angle = self.rotation_rays + (math.tau / self.symmetry) * i
                color = palette_gradient(self.palette, i / self.symmetry + t * 0.03)
                alpha = int(220 * visible)
                end = (self.center[0] + math.cos(angle) * length,
                       self.center[1] + math.sin(angle) * length)
                pygame.draw.line(surface, (*color, alpha), self.center, end, width=4)
        except Exception:
            pass

    # ---- Layer 4: harmonische Blaetter -> harmonic_energy ----
    def draw_petals(self, surface, t, activity, dt):
        try:
            visible = smoothstep(activity, 0.18, 0.53)
            if visible <= 0.01:
                return
            self.rotation_petals -= dt * (0.08 + activity * 0.25)
            petal_count = max(4, self.symmetry // 2)
            radius = self.max_radius * (0.35 + activity * 0.45)
            petal_len = max(20, self.max_radius * 0.38 * (0.5 + activity))
            for i in range(petal_count):
                angle = self.rotation_petals + (math.tau / petal_count) * i
                cx = self.center[0] + math.cos(angle) * radius
                cy = self.center[1] + math.sin(angle) * radius
                color = palette_gradient(self.palette, i / petal_count + t * 0.02 + 0.5)
                alpha = int(160 * visible)
                petal_surf = pygame.Surface((petal_len, petal_len * 0.55), pygame.SRCALPHA)
                pygame.draw.ellipse(petal_surf, (*color, alpha), petal_surf.get_rect())
                rotated = pygame.transform.rotate(petal_surf, -math.degrees(angle))
                surface.blit(rotated, rotated.get_rect(center=(cx, cy)))
        except Exception:
            pass

    # ---- Layer 5: Chroma-Farbrad -> Tonhoehen-Energie ----
    def draw_chroma_wheel(self, surface, t, chroma_vector):
        try:
            radius = self.max_radius * 0.88
            n = len(chroma_vector)
            cx, cy = surface.get_rect().center

            for i, value in enumerate(chroma_vector):
                if value < 0.25:
                    continue
                angle = (math.tau / n) * i
                color = palette_gradient(self.palette, i / n + t * 0.015)
                alpha = int(200 * min(1.0, value))
                length = radius * (0.20 + value * 0.40)
                inner, outer = radius - length / 2, radius + length / 2

                p1 = (cx + math.cos(angle) * inner, cy + math.sin(angle) * inner)
                p2 = (cx + math.cos(angle) * outer, cy + math.sin(angle) * outer)

                p1_int = (int(p1[0]), int(p1[1]))
                p2_int = (int(p2[0]), int(p2[1]))

                pygame.draw.line(surface, (*color, alpha), p1_int, p2_int, width=8)
        except Exception:
            pass

    # ---- Layer 6: Funken -> Rolloff / Noisiness (Treble) ----
    def maybe_spawn_sparks(self, t, activity):
        try:
            if activity < 0.35:
                return
            if random.random() < activity * 0.5:
                angle = random.uniform(0, math.tau)
                radius = self.max_radius * random.uniform(0.65, 1.15)
                color = palette_gradient(self.palette, random.random())
                self.sparks.append(Spark(t, angle, radius, color))
        except Exception:
            pass

    def draw_sparks(self, surface, t):
        try:
            cx, cy = surface.get_rect().center
            center_tuple = (cx, cy)
            self.sparks = [s for s in self.sparks if s.draw(surface, center_tuple, t)]
        except Exception:
            pass

    # ---- Layer 7: fliessende Wellen im Hintergrund -> Energie + Brightness ----
    def draw_waves(self, surface, t, energy, brightness):
        try:
            cx, cy = surface.get_rect().center

            for r_i in range(3):
                base_radius = self.max_radius * (0.45 + r_i * 0.22)
                points = []
                n_points = 60
                speed = 0.6 + brightness * 1.2
                for i in range(n_points + 1):
                    angle = (math.tau / n_points) * i
                    wobble = math.sin(angle * 5 + t * speed + r_i) * (10 + energy * 20)
                    r = base_radius + wobble

                    points.append((int(cx + math.cos(angle) * r),
                                   int(cy + math.sin(angle) * r)))

                if len(points) > 1:
                    color = palette_gradient(self.palette, 0.2 + r_i * 0.25 + t * 0.005)
                    alpha = int(45 - r_i * 10)
                    pygame.draw.polygon(surface, (*color, max(0, alpha)), points, width=3)
        except Exception:
            pass

    def draw(self, screen, t, dt, features):
        layer_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.draw_waves(layer_surf, t, features["energy"], features["brightness"])
        self.draw_chroma_wheel(layer_surf, t, features["chroma"])
        self.draw_petals(layer_surf, t, features["harmonic"], dt)
        self.draw_rays(layer_surf, t, features["percussive"], dt)
        self.draw_ripples(layer_surf, t)
        self.draw_sparks(layer_surf, t)
        self.draw_core(layer_surf, t, features["energy"])

        screen.blit(layer_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# ---- Startfunktion für den Visualizer (Hauptebene, außerhalb der Klasse) ----
def run_mandala(tempo, beat_times, filepath, colors=None, audio_features=None, width=1280, height=800):
    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Rave Visualizer - Mandala - {tempo:.1f} BPM")
    clock = pygame.time.Clock()

    visualizer = MandalaVisualizer(width, height, palette=colors)

    start_time = time.time()
    beat_index = 0
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if audio_features is not None:
            features = {
                "energy": audio_features.energy_at(t),
                "onset": audio_features.onset_at(t),
                "brightness": audio_features.brightness_at(t),
                "percussive": audio_features.percussive_onset_at(t),
                "harmonic": audio_features.harmonic_energy_at(t),
                "chroma": audio_features.chroma_at(t),
                "noisiness": audio_features.noisiness_at(t),
                "rolloff": audio_features.rolloff_at(t),
            }
        else:
            features = {
                "energy": 0.4, "onset": 0.0, "brightness": 0.4,
                "percussive": 0.0, "harmonic": 0.3,
                "chroma": [0.0] * 12, "noisiness": 0.2, "rolloff": 0.3,
            }

        if beat_index < len(beat_times) and t >= beat_times[beat_index]:
            visualizer.spawn_ripple(t)
            beat_index += 1

        visualizer.maybe_spawn_sparks(t, max(features["rolloff"], features["noisiness"]))

        screen.fill((6, 4, 12))
        visualizer.draw(screen, t, dt, features)
        pygame.display.flip()

    pygame.quit()