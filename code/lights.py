import random
from multiprocessing import Process


class Lights(Process):

    def __init__(self, lights_array, lights_array_lock, key_queues):
        super().__init__()
        self.traffic_lights = lights_array
        self.keyQueues = key_queues
        self.lock = lights_array_lock

    def run(self):
        if sig == signal.SIGUSR1:
            return
