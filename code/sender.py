import time
from queue import Empty
from multiprocessing import Process, Queue
import socket

PORT_SENDER = 2025
HOST_SENDER = "localhost"

class Sender(Process):
    def __init__(self, sent_messages_queue:Queue):
        super(Sender, self).__init__()
        self.sent_messages_queue = sent_messages_queue
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST_SENDER, PORT_SENDER))
        self.server_socket.listen(10)
        self.clients = []
        self.server_socket.setblocking(False)  # Set server socket to non-blocking

    def run(self):
        while True:
            # Check if there's a message to send
            try:
                message = self.sent_messages_queue.get_nowait()
                # Iterate through a copy in case the list changes during iteration
                for client in list(self.clients):
                    try:
                        client.send(message.encode('utf-8'))
                    except BrokenPipeError:
                        # Client disconnected; remove from the list
                        self.clients.remove(client)
            except Empty:
                # No messages to send; proceed to check for new connections
                pass

            # Attempt to accept new connections in a non-blocking way
            try:
                client_socket, addr = self.server_socket.accept()
                client_socket.setblocking(False)
                self.clients.append(client_socket)
            except BlockingIOError:
                # No pending connections; continue the loop
                pass
            except Exception as e:
                # Handle any other exceptions that may occur
                print(f"Exception occurred: {e}")

            # Sleep briefly to prevent high CPU usage
            time.sleep(0.001)