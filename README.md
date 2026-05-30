# Bachelor_project
A software-based modem for underwater acoustic communication, designed to run on a Raspberry Pi 5. The system encodes and transmits data using (FSK) at 40 kHz and 44 kHz, and decodes incoming signals using (STFT) analysis. Received data is forwarded over TCP through a Tailscale mesh VPN to a remote endpoint via a Starlink satellite connection.

Underwater Acoustic Communication System
A Python-based software-defined modem for underwater acoustic communication, built and tested on a Raspberry Pi 5. The system forms part of a satellite relay chain designed to bridge the gap between subsea acoustic sensors and a remote endpoint anywhere in the world. It handles everything from FSK signal generation and transmission, through acoustic reception and decoding, to forwarding the recovered data over TCP via a Tailscale mesh VPN and a Starlink satellite connection.
This project was developed as part of a bachelor thesis in electronics engineering, focused on building a working prototype of an autonomous maritime relay system for subsea sensor data.

Overview
Underwater acoustic communication is fundamentally different from conventional wireless communication. Radio waves do not propagate well through water, so sound is used instead. This comes with its own set of challenges: limited bandwidth, multipath reflections, Doppler shifts, and a noisy ambient environment. This project takes a software-defined approach to tackle these challenges, implementing the full modem stack in Python and keeping the hardware as simple as possible.
The result is a system that can transmit binary data acoustically at 500 bits per second, decode it reliably on the receive side using Short-Time Fourier Transform analysis, and forward the recovered data over a secure TCP connection to a remote server — regardless of where that server is located.
