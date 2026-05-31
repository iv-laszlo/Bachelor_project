import socket

SERVER_IP = "X.X.X.X"  # laptop IP
PORT = 5000

print("Creating socket...")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting...")
client.connect((SERVER_IP, PORT))

print("Connected to server")

while True:
    msg = input("Message: ")
    client.sendall(msg.encode())

    data = client.recv(1024)
    print("Server reply:", data.decode())

client.close()