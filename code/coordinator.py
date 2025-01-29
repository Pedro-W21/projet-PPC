import random
from multiprocessing import Process


class Coordinator(Process):

    def __init__(self, compteur_normal, lock_normal, compteur_prio, lock_prio, traffic_lights, traffic_lights_lock, keyQueues):
        super().__init__()
        self.compteur_normal = compteur_normal
        self.lock_normal = lock_normal
        self.compteur_prio = compteur_prio
        self.lock_prio = lock_prio
        self.traffic_lights = traffic_lights
        self.traffic_lights_lock = traffic_lights_lock
        self.keyQueues = keyQueues
