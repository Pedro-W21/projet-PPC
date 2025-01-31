import socket

HOST = "localhost"
PORT = 2025

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        while True:
            data = client_socket.recv(1024)
            print("DATA : ", data.decode())