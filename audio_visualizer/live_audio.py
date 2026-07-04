import pyaudio
import numpy as np
from scipy.fft import fft

# Audio settings
CHUNK = 512  # small chunk = fast response
RATE = 44100  # standard sample rate
CHANNELS = 1  # mono input


def get_frequency_bands(stream):
    # Read a chunk of audio
    data = stream.read(CHUNK, exception_on_overflow=False)

    # Convert raw bytes to numbers
    samples = np.frombuffer(data, dtype=np.int16)

    # Run FFT to get frequency content
    fft_result = np.abs(fft(samples))

    # Only use first half (second half is a mirror)
    fft_result = fft_result[:CHUNK // 2]

    # Calculate frequency resolution
    freq_resolution = RATE / CHUNK

    # Split into bands
    bass = np.mean(fft_result[int(20 / freq_resolution):int(200 / freq_resolution)])
    mid = np.mean(fft_result[int(200 / freq_resolution):int(2000 / freq_resolution)])
    treble = np.mean(fft_result[int(2000 / freq_resolution):int(8000 / freq_resolution)])

    return bass, mid, treble


def open_stream():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    return p, stream