import socket
import curses

HOST = "localhost"
PORT = 2025

class Display:
    def __init__(self, stdscr, display_width:int, display_height:int):

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cars_per_road = [0, 0, 0, 0]
        self.prio_cars_per_road = [0, 0, 0, 0]
        self.display_width = display_width
        self.display_height = display_height
        self.someone_passing = 0
        self.traffic_signals = [0, 0, 0, 0]
        self.stdscr = stdscr
        print("Connection réussie")
    def handle_message(self, message:str):
        parts = message.split("\n")
        if parts[0] == "NEW":
            car_index = int(parts[2])
            if parts[-1] == "1":
                self.cars_per_road[car_index] += 1
            elif parts[-1] == "2":
                self.prio_cars_per_road[car_index] += 1
        elif parts[0] == "PASSED":
            car_index = int(parts[2])
            if parts[-1] == "1":
                if self.cars_per_road[car_index] > 0:
                    self.cars_per_road[car_index] -= 1
                self.someone_passing = 1
            elif parts[-1] == "2":
                if self.prio_cars_per_road[car_index] > 0:
                    self.prio_cars_per_road[car_index] -= 1
                self.someone_passing = 2
    def full_refresh(self):
        pass

    def listening_loop(self):
        while True:
            data = self.client_socket.recv(1024)
            print("DATA : ", data.decode())


def main(stdscr):
    if __name__ == "__main__":
        client = Display(stdscr, 100, 100)
        client.listening_loop()

curses.wrapper(main)
        
        