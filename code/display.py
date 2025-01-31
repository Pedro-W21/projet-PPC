import socket

HOST = "localhost"
PORT = 2025

class Display:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connection réussie")

    def listening_loop(self):
        while True:
            data = self.client_socket.recv(1024)
            print("DATA : ", data.decode())

if __name__ == "__main__":
    client = Display()
    client.listening_loop()
        
        