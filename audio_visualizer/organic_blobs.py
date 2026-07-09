"""
Option 1: Organische Blob-Visualisierung (Wellenlinien-Prototyp).
Drei weiche Blobs mit permanentem Trail-Schimmer.
Elegante, träge und fließende Wellenbewegung ohne zittrige Aggressivität.
"""

import pygame
import random
import math
import time


class Blob:
    def __init__(self, x, y, radius, color, num_points=40): # Mehr Punkte für rundere Kurven
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.num_points = num_points

        # Flüssige, etwas langsamere Bewegung über den Screen
        self.vx = random.uniform(-35, 35)
        self.vy = random.uniform(-35, 35)

        # Offsets für die ungleichmäßige Wellen-Deformation (deutlich verlangsamt für Eleganz)
        self.noise_offsets = [random.uniform(0, math.tau) for _ in range(num_points)]
        self.noise_speeds = [random.uniform(0.4, 0.9) for _ in range(num_points)]

        self.pulse = 0.0
        self.wave_phase = 0.0
        self.split_cooldown = 0.0
        self.merge_cooldown = 0.0

        # Takt-Gedächtnis: Speichert den Beat-Zähler des letzten Splits
        self.last_split_beat = -99

    def update(self, dt, width, height, energy):
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Sanftes Abprallen an den Rändern
        margin = max(30.0, self.radius * 1.5)
        if self.x < margin or self.x > width - margin:
            self.vx *= -1
            self.x = max(margin, min(width - margin, self.x))
        if self.y < margin or self.y > height - margin:
            self.vy *= -1
            self.y = max(margin, min(height - margin, self.y))

        # Sanftere Puls-Dämpfung für elastisches "Ausklingen"
        self.pulse *= 0.94
        self.split_cooldown = max(0.0, self.split_cooldown - dt)
        self.merge_cooldown = max(0.0, self.merge_cooldown - dt)

        # Animations-Phase für das Wandern der Linien (ruhiger getaktet)
        self.wave_phase += dt * (0.5 + energy * 0.8)

    def trigger_pulse(self, strength=1.0):
        self.pulse = min(self.pulse + strength * 0.9, 2.5)

    def draw_waves(self, surface, t, speed_mult=1.0, global_scale=1.0, brightness=0.4, onset=0.0):
        num_waves = 5
        eff_base_radius = self.radius * global_scale * (1.0 + self.pulse * 0.12)

        for w in range(num_waves):
            wave_factor = ((w + self.wave_phase) % num_waves) / num_waves
            scale_multiplier = 1.0 + math.pow(wave_factor, 1.4) * 2.0
            wave_radius = eff_base_radius * scale_multiplier

            alpha = int(max(0, min(255, (1.0 - wave_factor) * 180)))
            if alpha < 5:
                continue

            points = []
            for i in range(self.num_points):
                angle = (i / self.num_points) * math.tau

                # FLÜSSIGER EFFEKT: Wir nutzen eine harmonische, wandernde Welle basierend auf dem Winkel (i),
                # statt jeden Punkt komplett unabhängig zittern zu lassen.
                wobble_speed = self.noise_speeds[i] * speed_mult * 0.5

                # Sanftes, elastisches Schwellen statt aggressiver Deformation
                distortion = 0.08 + (onset * 0.08)

                # Kombiniert raum- und zeitabhängige Sinuswellen für zähflüssiges Morphen
                harmonic_wave = math.sin(angle * 3.0 + t * 1.5) * 0.4
                individual_wobble = math.sin(t * wobble_speed + self.noise_offsets[i]) * 0.6

                wobble = (harmonic_wave + individual_wobble) * distortion
                r = wave_radius * (1.0 + wobble)

                px = self.x + math.cos(angle) * r
                py = self.y + math.sin(angle) * r
                points.append((px, py))

            if len(points) > 2:
                color_with_alpha = (*self.color, alpha)
                thickness = max(1, int(2 * (1.0 - wave_factor * 0.4)))
                pygame.draw.polygon(surface, color_with_alpha, points, thickness)


class BlobVisualizer:
    def __init__(self, width, height, palette):
        self.width = width
        self.height = height
        self.palette = palette
        self.blobs = []
        self.beat_count = 0

        # Start mit 3 Haupt-Blobs
        num_start_blobs = 3
        for i in range(num_start_blobs):
            x = self.width * (0.25 + i * 0.25)
            y = self.height * random.uniform(0.4, 0.6)
            radius = random.uniform(65, 85)
            color = self.palette[i % len(self.palette)]
            self.blobs.append(Blob(x, y, radius, color))

    def on_beat(self, strength=1.0):
        self.beat_count += 1
        for blob in self.blobs:
            blob.trigger_pulse(strength)

        # Aufspalten erst nach 5 Takten erlaubt
        if len(self.blobs) < 10:
            self._split_largest_blob()

    def _split_largest_blob(self):
        candidates = [
            b for b in self.blobs
            if b.radius > 35
            and b.split_cooldown <= 0
            and (self.beat_count - b.last_split_beat) >= 5
        ]

        if not candidates:
            return

        old_blob = max(candidates, key=lambda b: b.radius)

        old_blob.last_split_beat = self.beat_count
        old_blob.split_cooldown = 2.5

        new_radius = old_blob.radius * 0.65
        old_blob.radius = new_radius

        angle = random.uniform(0, math.tau)
        push_dist = new_radius * 1.2
        nx = old_blob.x + math.cos(angle) * push_dist
        ny = old_blob.y + math.sin(angle) * push_dist

        child_blob = Blob(nx, ny, new_radius, old_blob.color)
        child_blob.last_split_beat = self.beat_count
        child_blob.split_cooldown = 2.5

        # Etwas weicheres Davondriften nach dem Split
        speed = 70.0
        child_blob.vx, child_blob.vy = math.cos(angle) * speed, math.sin(angle) * speed
        old_blob.vx, old_blob.vy = -math.cos(angle) * speed, -math.sin(angle) * speed

        old_blob.merge_cooldown = 1.5
        child_blob.merge_cooldown = 1.5

        self.blobs.append(child_blob)

    def _try_merge_blobs(self, energy):
        if energy >= 0.75 or len(self.blobs) <= 3:
            return

        for i, b1 in enumerate(self.blobs):
            if b1.merge_cooldown > 0:
                continue
            for b2 in self.blobs[i + 1:]:
                if b2.merge_cooldown > 0 or b1.color != b2.color:
                    continue

                dist = math.hypot(b1.x - b2.x, b1.y - b2.y)

                if dist < (b1.radius + b2.radius) * 1.8:
                    total_area = (b1.radius ** 2) + (b2.radius ** 2)
                    b1.radius = min(100.0, math.sqrt(total_area))

                    b1.x = (b1.x + b2.x) / 2
                    b1.y = (b1.y + b2.y) / 2

                    b1.trigger_pulse(0.5)
                    b1.merge_cooldown = 1.5

                    b1.last_split_beat = self.beat_count - 2

                    self.blobs.remove(b2)
                    return

    def micro_pulse(self, strength):
        for blob in self.blobs:
            blob.trigger_pulse(strength * 0.3)

    def update(self, dt, energy=0.3):
        for blob in self.blobs:
            blob.update(dt, self.width, self.height, energy)
        self._try_merge_blobs(energy)

    def draw(self, screen, t, breathing=1.0, speed_mult=1.0, brightness=0.4, onset=0.0):
        glow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for blob in self.blobs:
            blob.draw_waves(glow_surf, t, speed_mult=speed_mult, global_scale=breathing, brightness=brightness, onset=onset)
        screen.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def update_and_draw(self, surface, t, dt, features):
        self.width, self.height = surface.get_size()
        energy = features.get("energy", 0.3)
        onset = features.get("onset", 0.0)
        brightness = features.get("brightness", 0.4)

        self.update(dt, energy=energy)

        breathing = 1.0 + energy * 0.20
        speed_mult = 0.4 + brightness * 1.0 # Obergrenze der Geschwindigkeit gedrosselt

        self.draw(surface, t, breathing=breathing, speed_mult=speed_mult, brightness=brightness, onset=onset)


def run_blobs(tempo, beat_times, filepath, colors=None, audio_features=None, width=1280, height=800):
    if colors is None:
        colors = [(150, 50, 255), (0, 255, 255), (255, 0, 150)]

    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(filepath)
    pygame.mixer.music.play()

    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption(f"Rave Visualizer - Linien-Blobs Prototyp")
    clock = pygame.time.Clock()

    visualizer = BlobVisualizer(width, height, palette=colors)
    screen.fill((6, 4, 12))

    start_time = time.time()
    beat_index = 0
    onset_cooldown = 0.0
    running = True

    while running:
        dt = max(0.001, clock.tick(60) / 1000.0)
        t = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                screen.fill((6, 4, 12))

        if audio_features is not None:
            features = {
                "energy": audio_features.energy_at(t),
                "onset": audio_features.onset_at(t),
                "brightness": audio_features.brightness_at(t)
            }
        else:
            features = {"energy": 0.4, "onset": 0.0, "brightness": 0.4}

        if beat_index < len(beat_times) and t >= beat_times[beat_index]:
            visualizer.on_beat(strength=1.0 + features["energy"])
            beat_index += 1

        onset_cooldown -= dt
        if onset_cooldown <= 0 and features["onset"] > 0.55:
            visualizer.micro_pulse(strength=features["onset"])
            onset_cooldown = 0.05

        # Trail-Effekt für den glühenden Vektorschweif
        trail_surf = pygame.Surface((width, height))
        trail_surf.set_alpha(35) # Leicht verringert für seidenweichere Schweife
        trail_surf.fill((6, 4, 12))
        screen.blit(trail_surf, (0, 0))

        visualizer.update_and_draw(screen, t, dt, features)
        pygame.display.flip()

    pygame.quit()