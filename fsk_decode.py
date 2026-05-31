import argparse
import logging
import numpy as np
from scipy.io import wavfile
import librosa
import librosa.display
from scipy.signal import butter, sosfiltfilt
import wave
import matplotlib.pyplot as plt


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    if lowcut <= 0 or highcut >= nyq or lowcut >= highcut:
        logging.error("Invalid filter cutoff frequencies. Check lowcut and highcut values.")
        return None
    sos = butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos') #Use SOS for numerical stability
    y = sosfiltfilt(sos, data) # Use sosfiltfilt for zero-phase filtering
    return y

def decode_fsk(file_path, frequency, deviation, bit_duration):
    resample_rate = 200000
    sr = 192000
    data =  np.loadtxt(file_path)

    nyquist_frequency = sr / 2
    if frequency + deviation > nyquist_frequency:
        logging.error(f"Carrier frequency + deviation ({frequency + deviation} Hz) exceeds the Nyquist frequency ({nyquist_frequency} Hz). Reduce the carrier frequency or increase the sample rate.")
        return

    lowcut = frequency - deviation - 200
    highcut = frequency + deviation + 200
    print('number of samples in file: ',len(data))
    filtered_data = butter_bandpass_filter(data, lowcut, highcut, sr)
    if filtered_data is None:
        return

    window_size = int(bit_duration * sr)
#    hop_length = int(window_size // 4)
    hop_length = window_size       #if hop_length = window_size the windows are not overlapping
    print('sr: ',sr)

    stft = librosa.stft(filtered_data, n_fft=window_size, hop_length=hop_length, window='hann', center=False)
    magnitudes = np.abs(stft)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=window_size)
    # ... (rest of the decode_fsk function remains the same)
    print('dimension_magnitudes_column: ',magnitudes.shape[0])   # stft coefficients
    print('dimension_magnitudes_rows: ',magnitudes.shape[1])     # number of windows

# ... (rest of the code remains the same)
    decoded_data = ""
    samples_per_bit = int(sr * bit_duration)
    num_frames = int(np.ceil(len(filtered_data) / samples_per_bit)) # Corrected frame calculation
    print('num_bits: ',num_frames)
    print('bit_duration: ',bit_duration)
    for i in range(num_frames):
        start_sample = i * samples_per_bit
        end_sample = min((i + 1) * samples_per_bit, len(filtered_data))
        if start_sample >= len(filtered_data) or start_sample == end_sample:
            continue

        frame_magnitudes = magnitudes[:, int(start_sample / hop_length):int(end_sample / hop_length)]
        if frame_magnitudes.size == 0:
            continue

        avg_magnitudes = np.mean(frame_magnitudes, axis=1) # count magnitude average of all windows in 1 bit duration
        peak_index = np.argmax(avg_magnitudes)             # find maximum magnitude in 1 bit duration
        peak_frequency = frequencies[peak_index]           # find the frequency for maximum magnitude
        logging.debug(f"Frame {i}: Peak frequency = {peak_frequency:.2f} Hz") #Added logging

        if peak_frequency > frequency + deviation / 2:
            decoded_data += "1"
        else:
            decoded_data += "0"

    num_bits = len(decoded_data)
    total_duration = num_bits * bit_duration
    num_samples = len(data)

    logging.info(f"Decoded data: {decoded_data}")
    logging.info(f"Number of bits: {num_bits}")
    logging.info(f"Total duration: {total_duration:.4f} seconds")
    logging.info(f"Number of samples: {num_samples}")
    logging.info(f"Sample rate used: {sr} Hz")
    logging.info(f"Frequency used: {frequency} Hz")
    logging.info(f"Deviation used: {deviation} Hz")

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.power_to_db(magnitudes, ref=np.max),
                             sr=sr, x_axis='ms', y_axis='hz',n_fft=window_size, hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('FSK Spectrogram')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Decode FSK signal')
    parser.add_argument('file_path', type=str, help='Path to the WAV file')
    parser.add_argument('--frequency', type=float, required=True, help='Carrier frequency in Hz')
    parser.add_argument('--deviation', type=float, required=True, help='Frequency deviation in Hz')
    parser.add_argument('--baud-rate', type=float, required=True, help='Baud rate')
    parser.add_argument('--debug', type=int, default=20, choices=[10, 20, 30, 40, 50], help='Debug level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL)')
    args = parser.parse_args()

    numeric_level = args.debug
    logging.basicConfig(level=numeric_level)

    bit_duration = 1.0 / args.baud_rate
    decode_fsk(args.file_path, args.frequency, args.deviation, bit_duration)