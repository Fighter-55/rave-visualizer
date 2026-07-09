"""
Dispatcher: leitet an die jeweils gewaehlte Visualisierungs-Option weiter.
Neue Optionen werden hier einfach als weiterer 'elif mode == ...' Zweig ergaenzt.
"""


def run(tempo, beat_times, filepath, mode="mandala", colors=None, audio_features=None, width=1280, height=800):
    if mode == "blobs":
        from organic_blobs import run_blobs
        run_blobs(tempo, beat_times, filepath, colors=colors, audio_features=audio_features, width=width, height=height)
    elif mode == "mandala":
        from mandala import run_mandala
        run_mandala(tempo, beat_times, filepath, colors=colors, audio_features=audio_features, width=width, height=height)
    else:
        raise ValueError(f"Unbekannter Visualisierungs-Modus: {mode}")
