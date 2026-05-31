import numpy as np
import sounddevice as sd

# Signal parameters
fs = 192000          # sample rate (supported by HiFiBerry DAC)
freq = 10000          # sine frequency (Hz)
amplitude = 0.5      # 0.0–1.0 (avoid clipping)

# Generate continuous buffer
t = np.arange(0, fs) / fs
wave = amplitude * np.sin(2 * np.pi * freq * t)

# Stream callback (loops forever)
def callback(outdata, frames, time, status):
    global wave
    outdata[:] = wave[:frames].reshape(-1, 1)

# Start output stream
with sd.OutputStream(samplerate=fs, channels=1, callback=callback):
    print("Sine wave running... Ctrl+C to stop")
    while True:
        pass
