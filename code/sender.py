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
            try:
                message = self.sent_messages_queue.get_nowait()
                # on itère sur une copie pour pouvoir remove sans problèmes pendant l'itération
                for client in list(self.clients):
                    try:
                        
                        client.send(message.encode('utf-8'))
                    except BrokenPipeError:
                        self.clients.remove(client)
                    except ConnectionResetError:
                        self.clients.remove(client)
                    except ConnectionAbortedError:
                        self.clients.remove(client)
                    except ConnectionRefusedError:
                        self.clients.remove(client)
            except Empty:
                pass

            try:
                client_socket, addr = self.server_socket.accept()
                client_socket.setblocking(False)
                self.clients.append(client_socket)
            except BlockingIOError:
                # pas de nouvelles connections, on continue
                pass
            except Exception as e:
                print(f"Exception occurred: {e}")
            
            time.sleep(0.001)