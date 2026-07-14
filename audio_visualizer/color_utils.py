#"""Hilfsfunktionen fuer fliessende Farbverlaeufe auf Basis der gewaehlten Presets."""


def lerp_color(c1, c2, f):
    f = max(0.0, min(1.0, f))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * f) for i in range(3))


def palette_gradient(palette, f):

    n = len(palette)
    f = f % 1.0
    scaled = f * n
    idx = int(scaled) % n
    frac = scaled - int(scaled)
    return lerp_color(palette[idx], palette[(idx + 1) % n], frac)
