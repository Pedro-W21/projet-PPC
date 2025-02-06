from multiprocessing import Process, Lock
import sysv_ipc
import random
import time
from math import sin

class Priority(Process):

    def __init__(self, compteur_global, keyQueues, lock_compteur_global, sent_messages_queue, static_time_scale, static_time_scale_lock, variable_time_scale, variable_time_scale_lock, prio_cars_per_road):
        super().__init__()
        self.keyQueues = keyQueues
        self.lock_compteur_global = lock_compteur_global
        self.compteur_global = compteur_global #compteur global de nombre de voitures prioritaires
        self.id = 0
        self.messageQueues = [sysv_ipc.MessageQueue(key) for key in keyQueues]
        self.sent_messages_queue = sent_messages_queue
        self.static_time_scale = static_time_scale
        self.static_time_scale_lock = static_time_scale_lock
        self.variable_time_scale = variable_time_scale
        self.variable_time_scale_lock = variable_time_scale_lock
        self.start_time = time.time()
        self.prio_cars_per_road = prio_cars_per_road

    def run(self):
        while True:
            #on regarde une première fois le compteur global
            with self.lock_compteur_global:
                    compteur_temporaire = self.compteur_global.value
            #boucle principale
            
            if compteur_temporaire <= 8:
                #print("TICK PRIORITY")
                #print(f"PRIO AT {compteur_temporaire}")
                #choisit de manière random où mettre une voiture
                depart = random.randint(0,3)
                arrivee = random.randint(0,3)
                #pour éviter que le chemin du départ soit l'arrivée
                while arrivee == depart :
                    arrivee = random.randint(0,3)
                texte = f"{self.id}_{depart}_{arrivee}"
                #print("adding prio", texte)
                mq = self.messageQueues[depart]
                mq.send(texte.encode(), type=2)
                self.sent_messages_queue.put(f"NEW {self.id} {depart} {arrivee} 2 {compteur_temporaire}")
                with self.lock_compteur_global:
                    self.compteur_global.value += 1
                    self.prio_cars_per_road[depart] += 1
                self.id += 1

            # On a pas besoin de la plus grande précision possible sur la valeur des échelles de temps, c'est pas grave si on exécute quelques tick trop vite ou trop lentement
            with self.static_time_scale_lock:
                static_time_scale = self.static_time_scale.value
            with self.variable_time_scale_lock:
                variable_time_scale = self.variable_time_scale.value
            right_now = time.time()
            time.sleep(abs(sin((right_now - self.start_time) * variable_time_scale * 0.5)) * variable_time_scale + static_time_scale * 0.4)
