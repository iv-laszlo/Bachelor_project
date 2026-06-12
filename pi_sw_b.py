import socket
import numpy as np
import librosa
import librosa.display
from scipy.signal import butter, sosfiltfilt
import matplotlib.pyplot as plt
import time

deviation = 2000 #frequency Hz
main_frequency = 42000 #frequency Hz
sample_rate = 192000
baud_rate = 500

SERVER_IP = "192.160.0.24"  # laptop IP
PORT = 5000

def generate_fsk_signal(bits, main_frequency, deviation, baud_rate, sample_rate):
    """Generates an FSK signal from a binary string using baud rate."""
    try:
        if not all(bit in '01' for bit in bits):
            return None

        bit_duration = 1.0 / baud_rate
        num_bits = len(bits)
        total_samples = int(num_bits * bit_duration * sample_rate)
        signal = np.zeros(total_samples)

        mark_frequency = main_frequency + deviation
        space_frequency = main_frequency - deviation

        sample_index = 0
        for bit in bits:
            frequency_to_use = mark_frequency if bit == '1' else space_frequency
            num_samples_per_bit = int(bit_duration * sample_rate)
            t = np.linspace(0, bit_duration, num_samples_per_bit, endpoint=False)
            sine_wave = np.sin(2 * np.pi * frequency_to_use * t)
            signal[sample_index:sample_index + num_samples_per_bit] = sine_wave
            sample_index += num_samples_per_bit

        return signal

    except Exception as e:
        return None

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    if lowcut <= 0 or highcut >= nyq or lowcut >= highcut:
        return None
    sos = butter(order, [lowcut, highcut], btype='band', fs=fs, output='sos') #Use SOS for numerical stability
    y = sosfiltfilt(sos, data) # Use sosfiltfilt for zero-phase filtering
    return y

def decode_fsk(file_path, frequency, deviation, bit_duration):
    start = time.time()
    sr = 192000
    data =  np.loadtxt(file_path)

    nyquist_frequency = sr / 2
    if frequency + deviation > nyquist_frequency:
        return

    lowcut = frequency - deviation - 200
    highcut = frequency + deviation + 200
    filtered_data = butter_bandpass_filter(data, lowcut, highcut, sr)
    if filtered_data is None:
        return

    window_size = int(bit_duration * sr)
#    hop_length = int(window_size // 4)
    hop_length = window_size       #if hop_length = window_size the windows are not overlapping

    stft = librosa.stft(filtered_data, n_fft=window_size, hop_length=hop_length, window='hann', center=False)
    magnitudes = np.abs(stft)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=window_size)
    # ... (rest of the decode_fsk function remains the same)


# ... (rest of the code remains the same)
    decoded_data = ""
    samples_per_bit = int(sr * bit_duration)
    num_frames = int(np.ceil(len(filtered_data) / samples_per_bit)) # Corrected frame calculation

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

        if peak_frequency > frequency + deviation / 2:
            decoded_data += "1"
        else:
            decoded_data += "0"

    num_bits = len(decoded_data)
    total_duration = num_bits * bit_duration
    num_samples = len(data)
    stop = time.time()
    decoding_time = round(stop-start,3)

    print(f"Decoded data: {decoded_data}")
    print(f"Number of bits: {num_bits}")
    print(f"Total duration: {total_duration:.4f} seconds")
    print(f"Number of samples: {num_samples}")
    print(f"Sample rate used: {sr} Hz")
    print(f"Frequency used: {frequency} Hz")
    print(f"Deviation used: {deviation} Hz")
    print(f"Decoding time: {decoding_time} s")
    print("---------------------------------------------------------------------------------------------------")

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(librosa.power_to_db(magnitudes, ref=np.max),
                             sr=sr, x_axis='ms', y_axis='hz',n_fft=window_size, hop_length=hop_length)
    plt.colorbar(format='%+2.0f dB')
    plt.title('FSK Spectrogram')
    plt.tight_layout()
    plt.show()

    return(decoded_data)

if __name__ == "__main__":

    print("---------------------------------------------------------------------------------------------------")
    message = input("Type in message:")
    print("---------------------------------------------------------------------------------------------------")
    ascii_values = [ord(char) for char in message]
    ascii_string=""
    checksum=0

    for i in ascii_values:
        ascii_string=ascii_string+(bin(i)[2:]).zfill(8)
        checksum=checksum+i

    checksum_bin=(bin(int(bin(checksum),2) & 0b11111111)[2:]).zfill(8)
    length = bin(len(ascii_values))
    data = "10101010" + length[2:].zfill(8) + ascii_string.ljust(472,"0") + checksum_bin + "1010"
    signal = generate_fsk_signal(data, main_frequency, deviation, baud_rate, sample_rate)

    if signal is not None:
        num_bits = len(data)
        bit_duration = 1.0 / baud_rate
        total_duration = num_bits * bit_duration
        num_samples = len(signal)
        print(f"Generated FSK signal for bits: {data}")
        print(f"Number of bits: {num_bits}")
        print(f"Total duration: {total_duration:.4f} seconds")
        print(f"Number of samples: {num_samples}")
        print(f"Baud rate used: {baud_rate} baud")
        print(f"Sample rate used: {sample_rate} Hz")
        print(f"Frequency used: {main_frequency} Hz")
        print(f"Deviation used: {deviation} Hz")
        print(f"Checksum used: {checksum_bin}")
        print("---------------------------------------------------------------------------------------------------")
        #save_wav_file(args.output, signal, args.sample_rate)

        outfile=open("output.txt","w")
        for i in signal:
            outfile.write(str(i) + "\n")
        outfile.close()

    rx_data=decode_fsk("output.txt", main_frequency, deviation, bit_duration)
    rx_data_len=int(rx_data[8:16],2)
    rx_data_payload=rx_data[16:rx_data_len*8+16]
    rx_data_checksum=rx_data[488:496]
    payload_string=[]
    i=0

    while(i<rx_data_len*8):
        payload_string.append(int(rx_data_payload[i:i+8],2))
        i=i+8

    rx_message=""
    for i in payload_string:
        rx_message=rx_message + chr(i)

    ascii_values_rx = [ord(char) for char in rx_message]
    rx_message_checksum = 0

    for i in ascii_values_rx:
        rx_message_checksum = rx_message_checksum + i

    rx_message_checksum_bin = (bin(int(bin(rx_message_checksum), 2) & 0b11111111)[2:]).zfill(8)

    print(f"Received checksum: {rx_data_checksum}")
    print(f"Calculated checksum: {rx_message_checksum_bin}")

    if rx_message_checksum_bin==rx_data_checksum:
        print("Checksum state: Correct")
    else:
        print("Checksum state: Incorrect")

    print("---------------------------------------------------------------------------------------------------")
    print(f"Received message: {rx_message}")
    print("---------------------------------------------------------------------------------------------------")

    print("Creating socket...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Connecting to server...")
    client.connect((SERVER_IP, PORT))
    print("Connected to server")

    client.sendall(rx_message.encode())

    data = client.recv(1024)
    print("Server reply:", data.decode())

    client.close()
