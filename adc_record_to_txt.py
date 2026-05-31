# adc_record_to_txt.py
import sounddevice as sd
import numpy as np

device_index = 0
fs = 192000
channels = 2
blocksize = 4096
duration_sec = 5
outfile = "adc_data_2.txt"

f = open(outfile, "w")

with sd.InputStream(device=device_index,
                    channels=channels,
                    samplerate=fs,
                    blocksize=blocksize) as stream:

    total_blocks = int(fs * duration_sec / blocksize)

    for _ in range(total_blocks):
        data, overflowed = stream.read(blocksize)

        # take one channel
        ch = data[:, 0]

        f.write("\n".join(map(str, ch)) + "\n")

f.close()
