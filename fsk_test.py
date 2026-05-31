import numpy as np
import sounddevice as sd

# =========================
# USER SETTINGS
# =========================

bit_string = "1010101010"

f0 = 40000        # Frequency for bit 0
f1 = 44000        # Frequency for bit 1

bit_duration = 0.01   # seconds per bit (10 ms = 100 bps)

sample_rate = 192000  # HiFiBerry DAC sample rate

amplitude = 0.3       # 0.0 to 1.0

# =========================
# GENERATE FSK SIGNAL
# =========================

samples_per_bit = int(bit_duration * sample_rate)

signal = np.array([], dtype=np.float32)

for bit in bit_string:

    if bit == '0':
        freq = f0
    else:
        freq = f1

    t = np.arange(samples_per_bit) / sample_rate

    sine = amplitude * np.sin(2 * np.pi * freq * t)

    signal = np.concatenate((signal, sine.astype(np.float32)))

# =========================
# PLAY THROUGH HIFIBERRY DAC
# =========================

print("Playing FSK signal...")
print("Bit string:", bit_string)

sd.play(signal, samplerate=sample_rate, blocking=True)

print("Done.")
