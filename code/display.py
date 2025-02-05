import socket
import curses

HOST = "localhost"
PORT = 2025

class Display:
    def __init__(self, stdscr:curses.window, display_width:int, display_height:int):
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.cars_per_road = [0, 0, 0, 0]
        self.prio_cars_per_road = [0, 0, 0, 0]
        self.display_width = display_width
        self.display_height = display_height
        self.someone_passing = 0
        self.traffic_signals = [0, 0, 0, 0]
        self.stdscr = stdscr
        self.smallest_dimension = display_width if display_width < display_height else display_height
        print("Connection réussie")
    def handle_message(self, message:str):
        parts = message.split(" ")
        self.last_parts = parts
        #counters_string = f"{parts}"
        #self.stdscr.addstr(self.smallest_dimension - 3, self.smallest_dimension - len(counters_string), counters_string)
        car_index = int(parts[2])
        if parts[0] == "NEW":
            if int(parts[-2]) == 1:
                self.cars_per_road[car_index] += 1
            elif int(parts[-2]) == 2:
                self.prio_cars_per_road[car_index] += 1
        elif parts[0] == "PASSED":
            if int(parts[-2]) == 1:
                self.cars_per_road[car_index] = int(parts[-1])
                self.someone_passing = 1
                self.traffic_signals[car_index] = 1
                self.traffic_signals[(car_index + 1) % len(self.traffic_signals)] = 0
                self.traffic_signals[(car_index + 2) % len(self.traffic_signals)] = 1
                self.traffic_signals[(car_index + 3) % len(self.traffic_signals)] = 0
            elif int(parts[-2]) == 2:
                self.prio_cars_per_road[car_index] = int(parts[-1])
                self.someone_passing = 2
                self.traffic_signals = [0, 0, 0, 0]
                self.traffic_signals[car_index] = 1
                self.prio_cars_per_road
    def full_refresh(self):
        """
        Your code goes here
        """
        middle = self.smallest_dimension // 2
        total_length = middle - 2
        x_prio = [middle - 1,  middle + 2, middle - 1, 0]
        y_prio = [0, middle - 1, middle + 2, middle - 1]

        x_norm = [middle, middle + 2, middle, 0]
        y_norm = [0, middle, middle + 2, middle]
        inverted = [False, True, True, False]

        traffic_lights_pos = [(middle - 3, middle - 2), (middle - 2, middle + 2), (middle + 2, middle + 2), (middle + 1, middle - 3)]
        for i in range(4):
            func = self.stdscr.vline if i % 2 == 0 else self.stdscr.hline
            empty_part_normal = (total_length - int(min(max((self.cars_per_road[i]/100) * total_length, 1), total_length))) if self.cars_per_road[i] != 0 else total_length
            empty_part_prio = (total_length - int(min(max((self.prio_cars_per_road[i]/20) * total_length, 1), total_length))) if self.prio_cars_per_road[i] != 0 else total_length
            y_add = 1 if i % 2 == 0 else 0
            x_add = 1 if i % 2 == 1 else 0
            if inverted[i]:
                first_part_normal = total_length - empty_part_normal
                first_part_prio = total_length - empty_part_prio
                func(y_norm[i], x_norm[i], "a", first_part_normal)
                func(y_prio[i], x_prio[i], "b", first_part_prio)
                func(y_norm[i] + first_part_normal*y_add, x_norm[i] + first_part_normal*x_add, "-", empty_part_normal)
                func(y_prio[i] + first_part_prio*y_add, x_prio[i] + first_part_prio*x_add, "-", empty_part_prio)
            else:
                func(y_norm[i], x_norm[i], "-", empty_part_normal)
                func(y_prio[i], x_prio[i], "-", empty_part_prio)
                func(y_norm[i] + empty_part_normal*y_add, x_norm[i] + empty_part_normal*x_add, "a", total_length - empty_part_normal)
                func(y_prio[i] + empty_part_prio*y_add, x_prio[i] + empty_part_prio*x_add, "b", total_length - empty_part_prio)
            if self.traffic_signals[i] == 0:
                self.stdscr.addstr(traffic_lights_pos[i][0], traffic_lights_pos[i][1], "R")
            else:
                self.stdscr.addstr(traffic_lights_pos[i][0], traffic_lights_pos[i][1], "G")
        if self.someone_passing != 0:
            self.stdscr.hline(middle-1, middle-1, str(self.someone_passing), 2)
            self.stdscr.hline(middle, middle-1, str(self.someone_passing), 2)
            self.someone_passing = 0
        else:
            self.stdscr.hline(middle-1, middle-1, " ", 2)
            self.stdscr.hline(middle, middle-1, " ", 2)

        #counters_string = f"{self.cars_per_road}"
        #self.stdscr.addstr(0, self.smallest_dimension - len(counters_string), counters_string)
        #counters_string = f"{self.prio_cars_per_road}"
        #self.stdscr.addstr(1, self.smallest_dimension - len(counters_string), counters_string)

        

        self.stdscr.refresh()
    def listening_loop(self):
        while True:
            data = self.client_socket.recv(1024)
            self.handle_message(data.decode())
            self.full_refresh()


def main(stdscr):
    if __name__ == "__main__":
        client = Display(stdscr, 20, 40)
        client.listening_loop()

curses.wrapper(main)
        
        