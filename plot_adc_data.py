import numpy as np
import matplotlib.pyplot as plt

# ======================
# CONFIG
# ======================
filename = "adc_data.txt"
fs = 192000

# ======================
# LOAD DATA
# ======================
data = np.loadtxt(filename)

if data.ndim > 1:
    data = data[:, 0]

# ======================
# PREPROCESSING (for nicer plot only)
# ======================

# 1. Remove DC offset
data = data - np.mean(data)

# 2. Simple smoothing filter (moving average)
window_size = 7
kernel = np.ones(window_size) / window_size
data_smooth = np.convolve(data, kernel, mode='same')

# 3. Downsample for visualization (important)
ds_factor = 10
data_vis = data_smooth[::ds_factor]

# New effective time axis
fs_vis = fs / ds_factor
t = np.arange(len(data_vis)) / fs_vis

# ======================
# TIME DOMAIN (CLEAN)
# ======================
plt.figure()
plt.plot(t[:2000], data_vis[:2000])
plt.title("Time Domain (Filtered + Downsampled)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

# ======================
# ZOOMED TIME DOMAIN PLOT
# ======================

data_zoom = data_vis  # already filtered + downsampled

# convert to time axis (important)
t = np.arange(len(data_zoom)) / fs_vis

# choose a small window to actually SEE sine waves
zoom_samples = int(200e-6 * fs_vis)   # 200 microseconds window

plt.figure()
plt.plot(t[:zoom_samples], data_zoom[:zoom_samples])
plt.title("Time Domain (Zoomed 40 kHz view)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)

# ======================
# CLEAN ZOOMED TIME DOMAIN (CENTERED)
# ======================

data_zoom = data_vis  # filtered + downsampled signal

N = len(data_zoom)

# Take middle portion (skip startup transients)
center = N // 2

# Window size: increase for more visible cycles
# 2 milliseconds gives many 40 kHz cycles (80 cycles approx)
window_time = 2e-3  # 2 ms
window_samples = int(window_time * fs_vis)

start = max(center - window_samples // 2, 0)
end = min(center + window_samples // 2, N)

t = np.arange(end - start) / fs_vis

plt.figure()
plt.plot(t, data_zoom[start:end])
plt.title("Time Domain (Centered, Stable Region)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)

# ======================
# CENTERED TIME DOMAIN + PEAK TIME LABELS
# ======================

data_zoom = data_vis

N = len(data_zoom)
center = N // 2

window_time = 2e-3  # 2 ms window
window_samples = int(window_time * fs_vis)

start = max(center - window_samples // 2, 0)
end = min(center + window_samples // 2, N)

segment = data_zoom[start:end]
t = np.arange(len(segment)) / fs_vis

# ----------------------
# Find peaks
# ----------------------
# simple peak detection (no scipy needed)
threshold = 0.7 * np.max(np.abs(segment))

peak_indices = np.where(np.abs(segment) > threshold)[0]

# keep only a few peaks (avoid clutter)
peak_indices = peak_indices[::max(1, len(peak_indices)//5)]

peak_times = t[peak_indices]
peak_values = segment[peak_indices]

# ----------------------
# Plot
# ----------------------
import matplotlib.pyplot as plt

plt.figure()
plt.plot(t, segment)

# mark peaks
plt.scatter(peak_times, peak_values, color='red')

# annotate time at peaks
for i in range(len(peak_times)):
    plt.text(
        peak_times[i],
        peak_values[i],
        f"{peak_times[i]*1e6:.1f} µs",
        fontsize=8,
        rotation=45
    )

plt.title("Time Domain (Centered + Peak Time Labels)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)

# ======================
# FFT (use raw or lightly windowed data)
# ======================
N = len(data)
window = np.hanning(N)
data_win = (data - np.mean(data)) * window

fft = np.fft.rfft(data_win)
freqs = np.fft.rfftfreq(N, d=1/fs)
magnitude = np.abs(fft)

peak_freq = freqs[np.argmax(magnitude)]
print("Peak frequency:", peak_freq, "Hz")

plt.figure()
plt.plot(freqs, magnitude)
plt.title("Frequency Spectrum (FFT)")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.xlim(0, 100000)

plt.show()