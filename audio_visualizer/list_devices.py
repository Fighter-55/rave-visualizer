import pyaudio

p = pyaudio.PyAudio()

print("Available audio input devices:\n")
for i in range(p.get_device_count()):
    device = p.get_device_info_by_index(i)
    if device['maxInputChannels'] > 0:
        print(f"  [{i}] {device['name']}")

p.terminate()