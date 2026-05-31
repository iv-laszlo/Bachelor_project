import socket

HOST = "0.0.0.0"   # listen on all interfaces
PORT = 5000

print("Creating socket...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Binding...")
server.bind((HOST, PORT))

print("Listening...")
server.listen(1)

print("Waiting for connection...")
print(f"Server listening on port {PORT}")

conn, addr = server.accept()
print("Connected by", addr)

while True:
    print("Waiting for data...")
    data = conn.recv(1024)
    if not data:
        print("Connection closed")
        break

    message = data.decode()
    print("Received:", message)

    reply = f"Echo: {message}"
    conn.sendall(reply.encode())

conn.close()
server.close()