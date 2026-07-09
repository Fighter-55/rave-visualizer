"""
Option 1: Organische Blob-Visualisierung.
Weiche, glow-artige "Ballons" die zum Beat pulsieren, sich aufspalten
und wieder zu groesseren Blobs verschmelzen. Reagiert zusaetzlich auf:
  - RMS-Energie      -> kontinuierliches "Atmen" (Groesse)
  - Onset-Strength    -> Mikro-Pulse zwischen den Haupt-Beats (Snares/Hats)
  - Spectral Centroid -> Wackel-Geschwindigkeit der Kontur (hell = nervoeser)
Farben kommen von aussen (z.B. color_menu.py) und werden hier nicht
durch Audio-Features veraendert.
"""

import pygame
import random
import math
import time


class Blob:
    def __init__(self, x, y, radius, color, num_points=18):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.num_points = num_points

        self.vx = random.uniform(-40, 40)   # px/sek
        self.vy = random.uniform(-40, 40)

        self.noise_offsets = [random.uniform(0, math.tau) for _ in range(num_points)]
        self.noise_speeds = [random.uniform(0.6, 1.6) for _ in range(num_points)]

        self.pulse = 0.0
        self.merge_cooldown = 0.0
        self.split_cooldown = 0.0

    def update(self, dt, width, height):
        self.x += self.vx * dt
        self.y += self.vy * dt

        margin = self.radius
        if self.x < margin or self.x > width - margin:
            self.vx *= -1
            self.x = max(margin, min(width - margin, self.x))
        if self.y < margin or self.y > height - margin:
            self.vy *= -1
            self.y = max(margin, min(height - margin, self.y))

        self.pulse *= 0.88
        self.merge_cooldown = max(0.0, self.merge_cooldown - dt)
        self.split_cooldown = max(0.0, self.split_cooldown - dt)

    def trigger_pulse(self, strength=1.0):
        self.pulse = min(self.pulse + strength, 2.2)

    def _contour_points(self, t, speed_mult=1.0, global_scale=1.0):
        points = []
        eff_radius = self.radius * (1 + self.pulse * 0.55) * global_scale
        for i in range(self.num_points):
            angle = (i / self.num_points) * math.tau
            wobble = math.sin(t * self.noise_speeds[i] * speed_mult + self.noise_offsets[i])
            r = eff_radius * (1 + wobble * 0.16)
            points.append((self.x + math.cos(angle) * r, self.y + math.sin(angle) * r))
        return points

    def draw(self, glow_surface, t, speed_mult=1.0, global_scale=1.0):
        points = self._contour_points(t, speed_mult, global_scale)
        for scale, alpha in ((1.35, 35), (1.15, 60), (1.0, 140)):
            scaled = [(self.x + (px - self.x) * scale, self.y + (py - self.y) * scale)
                      for px, py in points]
            pygame.draw.polygon(glow_surface, (*self.color, alpha), scaled)


class BlobVisualizer:
    def __init__(self, width, height, palette, num_blobs=7):
        self.width = width
        self.height = height
        self.palette = palette
        self.blobs = []
        for _ in range(num_blobs):
            self._spawn_blob()

    def _spawn_blob(self, x=None, y=None, radius=None):
        x = x if x is not None else random.uniform(120, self.width - 120)
        y = y if y is not None else random.uniform(120, self.height - 120)
        radius = radius if radius is not None else random.uniform(45, 95)
        color = random.choice(self.palette)
        self.blobs.append(Blob(x, y, radius, color))

    def on_beat(self, strength=1.0):
        """strength: 1.0 = normaler Beat, hoeher wenn zeitgleich viel Energie
        im Track ist -> heftigere Pulse und hoehere Split-Wahrscheinlichkeit."""
        for blob in self.blobs:
            blob.trigger_pulse(strength)

        split_chance = min(0.65, 0.2 + 0.25 * strength)
        if len(self.blobs) < 16 and random.random() < split_chance:
            self._split_random_blob()
        self._try_merge()

    def micro_pulse(self, strength):
        """Kleinere, haeufigere Pulse ausgeloest durch Onset-Strength
        (z.B. Hi-Hats/Snares zwischen den Haupt-Beats)."""
        if not self.blobs:
            return
        k = max(1, len(self.blobs) // 3)
        for blob in random.sample(self.blobs, k=k):
            blob.trigger_pulse(strength)

    def _split_random_blob(self):
        candidates = [b for b in self.blobs if b.radius > 38 and b.split_cooldown <= 0]
        if not candidates:
            return
        blob = random.choice(candidates)
        blob.split_cooldown = 2.0
        new_radius = blob.radius * 0.65
        blob.radius = new_radius

        angle = random.uniform(0, math.tau)
        nx = blob.x + math.cos(angle) * new_radius
        ny = blob.y + math.sin(angle) * new_radius
        self._spawn_blob(nx, ny, new_radius)

        new_blob = self.blobs[-1]
        speed = 60
        new_blob.vx, new_blob.vy = math.cos(angle) * speed, math.sin(angle) * speed
        blob.vx, blob.vy = -math.cos(angle) * speed, -math.sin(angle) * speed

        blob.merge_cooldown = 3.0
        new_blob.merge_cooldown = 3.0

    def _try_merge(self):
        if len(self.blobs) <= 3:
            return
        for i, b1 in enumerate(self.blobs):
            if b1.merge_cooldown > 0:
                continue
            for b2 in self.blobs[i + 1:]:
                if b2.merge_cooldown > 0:
                    continue
                dist = math.hypot(b1.x - b2.x, b1.y - b2.y)
                if dist < (b1.radius + b2.radius) * 0.4 and random.random() < 0.5:
                    total_area = b1.radius ** 2 + b2.radius ** 2
                    b1.radius = math.sqrt(total_area) * 0.9
                    b1.x, b1.y = (b1.x + b2.x) / 2, (b1.y + b2.y) / 2
                    b1.trigger_pulse(0.8)
                    self.blobs.remove(b2)
                    return

    def update(self, dt):
        for blob in self.blobs:
            blob.update(dt, self.width, self.height)

    def draw(self, screen, t, breathing=1.0, speed_mult=1.0):
        glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for blob in self.blobs:
            blob.draw(glow, t, speed_mult=speed_mult, global_scale=breathing)
        screen.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def run_blobs(tempo, beat_times, filepath, colors=None, audio_features=None,
              width=1280, height=800):
    """Startet die Blob-Visualisierung.
    colors: Liste von (r,g,b) Tupeln.
    audio_features: optionales AudioFeatures-Objekt aus audio.py fuer
                     Energie/Onset/Helligkeits-Reaktivitaet."""
    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f"Rave Visualizer - Organic Blobs - {tempo:.1f} BPM")
    clock = pygame.time.Clock()

    visualizer = BlobVisualizer(width, height, palette=colors)

    start_time = time.time()
    beat_index = 0
    onset_cooldown = 0.0
    running = True

    while running:
        dt = clock.tick(60) / 1000.0
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- Audio-Feature-Werte fuer den aktuellen Zeitpunkt ---
        if audio_features is not None:
            energy = audio_features.energy_at(t)
            onset = audio_features.onset_at(t)
            brightness = audio_features.brightness_at(t)
        else:
            energy, onset, brightness = 0.4, 0.0, 0.4

        # Haupt-Beat: kraeftiger Puls + evtl. Split, Staerke skaliert mit Energie
        if beat_index < len(beat_times) and t >= beat_times[beat_index]:
            visualizer.on_beat(strength=1.0 + energy)
            beat_index += 1

        # Onset-Strength: kleinere, haeufigere Zuckungen zwischen den Beats
        onset_cooldown -= dt
        if onset_cooldown <= 0 and onset > 0.55:
            visualizer.micro_pulse(strength=onset * 0.6)
            onset_cooldown = 0.06  # Mindestabstand, sonst zu hektisch bei 60fps

        # RMS-Energie -> kontinuierliches Atmen der Groesse
        breathing = 1.0 + energy * 0.22
        # Spectral Centroid -> Wackel-Tempo der Kontur (hell = nervoeser)
        speed_mult = 0.6 + brightness * 1.4

        visualizer.update(dt)

        fade = pygame.Surface((width, height))
        fade.set_alpha(45)
        fade.fill((0, 0, 0))
        screen.blit(fade, (0, 0))

        visualizer.draw(screen, t, breathing=breathing, speed_mult=speed_mult)
        pygame.display.flip()

    pygame.quit()
