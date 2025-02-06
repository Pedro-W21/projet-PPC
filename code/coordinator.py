import random
from multiprocessing import Process, Queue
import sysv_ipc
import signal
import os
import time

class Car:
    def __init__(self, car_type, id, start, end):
        self.car_type = car_type
        self.id = id
        self.start = start
        self.end = end

def car_from_string(car_message:str, car_type) -> Car:
    split_message = car_message.split("_")
    return Car(car_type, int(split_message[0]), int(split_message[1]), int(split_message[2]))

class Coordinator(Process):

    def __init__(self, compteur_normal, lock_normal, compteur_prio, lock_prio, traffic_lights, traffic_lights_lock, keyQueues, traffic_lights_pid, sent_message_queue, chemin_priorite_lock, mqpriorite, static_time_scale, static_time_scale_lock, variable_time_scale, variable_time_scale_lock, normal_cars_per_road, prio_cars_per_road):
        super().__init__()
        self.compteur_normal = compteur_normal
        self.lock_normal = lock_normal
        self.compteur_prio = compteur_prio
        self.lock_prio = lock_prio
        self.traffic_lights = traffic_lights
        self.traffic_lights_lock = traffic_lights_lock
        self.keyQueues = keyQueues
        self.message_queues = [sysv_ipc.MessageQueue(key) for key in keyQueues]
        self.hanging_normal_cars = [None for i in range(4)]
        self.hanging_prio_cars = [None for i in range(4)]
        self.traffic_lights_pid = traffic_lights_pid
        self.sent_messages_queue = sent_message_queue
        self.chemin_prio_lock = chemin_priorite_lock
        self.mq_priorite = mqpriorite
        self.tick = 0
        self.static_time_scale = static_time_scale
        self.static_time_scale_lock = static_time_scale_lock
        self.variable_time_scale = variable_time_scale
        self.variable_time_scale_lock = variable_time_scale_lock
        self.normal_cars_per_road = normal_cars_per_road
        self.prio_cars_per_road = prio_cars_per_road


    def send_car_passed(self, car:Car, val:int):
        self.sent_messages_queue.put(f"PASSED {car.id} {car.start} {car.end} {car.car_type} {val}")

    def run(self):
        
        while True:
            with self.static_time_scale_lock:
                static_time_scale = self.static_time_scale.value
            # décommenter la ligne suivante pour avoir une notion de la vitesse de la simulation à l'exécution
            #print(f"--------------------\n TICK COORD {self.tick}")
            self.tick += 1
            oldest_prio = None
            for i in range(4):
                # Si on a pas encore de voiture prioritaire "in flight" pour ce segment de route
                if self.hanging_prio_cars[i] == None:
                    # on essaie de récupérer la voiture prioritaire la plus vielle de la MessageQueue correspondante
                    try:
                        car_message, ty = self.message_queues[i].receive(type=2, block=False)
                        self.hanging_prio_cars[i] = car_from_string(car_message.decode(), ty)
                        # si il n'y a pas encore d'autre voiture prioritaire
                        if oldest_prio == None:
                            oldest_prio = i
                        # Si l'autre voiture prioritaire attend depuis moins longtemps et y'en a pas en attente à notre droite
                        elif self.hanging_prio_cars[i].id < self.hanging_prio_cars[oldest_prio].id and self.hanging_prio_cars[i-1] == None:
                            oldest_prio = i
                         
                    except sysv_ipc.BusyError:
                        pass
                # si il n'y a pas encore d'autre voiture prioritaire
                elif oldest_prio == None:
                    oldest_prio = i
                # Si l'autre voiture prioritaire attend depuis moins longtemps et y'en a pas en attente à notre droite
                elif self.hanging_prio_cars[i] != None and self.hanging_prio_cars[i].id < self.hanging_prio_cars[oldest_prio].id and self.hanging_prio_cars[i-1] == None:
                    oldest_prio = i
                
            if oldest_prio != None:
                with self.lock_prio:
                    self.compteur_prio.value -= 1
                    self.prio_cars_per_road[oldest_prio] -= 1
                    temp = self.prio_cars_per_road[oldest_prio]
                with self.chemin_prio_lock:
                    # on indique à Lights le chemin à rendre vert
                    self.mq_priorite.value = oldest_prio
                # send signal to Lights
                os.kill(self.traffic_lights_pid, signal.SIGUSR1)
                while True:
                        with self.chemin_prio_lock:
                            if self.mq_priorite.value == 5:
                                # Une fois qu'on est sûrs que les feux sont verts, on envoie la voiture
                                self.send_car_passed(self.hanging_prio_cars[oldest_prio], temp)
                                self.hanging_prio_cars[oldest_prio] = None
                                self.mq_priorite.value = 6
                                break
                        time.sleep(static_time_scale * 0.001)

                # On attend que Lights soit sorti de son handler avant de continuer
                while True:
                        with self.chemin_prio_lock:
                            if self.mq_priorite.value == 7:
                                break
                        time.sleep(static_time_scale * 0.001)
                
            else:
                with self.traffic_lights_lock:
                    oldest_passing_normal = None
                    for i in range(4):
                        # Si on a pas encore de voiture normale "in flight" pour ce segment de route
                        if self.hanging_normal_cars[i] == None:
                            # on essaie de récupérer la voiture normale la plus vieille de la MessageQueue correspondante
                            try:
                                car_message, ty = self.message_queues[i].receive(type=1, block=False)
                                self.hanging_normal_cars[i] = car_from_string(car_message.decode(), ty)
                                # si les lumières sont bonnes et on a pas d'autre voiture à faire passer
                                if oldest_passing_normal == None and self.traffic_lights[i]:
                                    oldest_passing_normal = i
                                # Sinon si l'autre voiture est plus jeune
                                elif oldest_passing_normal != None and self.hanging_normal_cars[i].id < self.hanging_normal_cars[oldest_passing_normal].id and self.traffic_lights[i]:
                                    oldest_passing_normal = i
                            except sysv_ipc.BusyError:
                                pass
                        
                        # si les lumières sont bonnes et on a pas d'autre voiture à faire passer
                        elif oldest_passing_normal == None and self.traffic_lights[i]:
                            oldest_passing_normal = i
                        # Sinon si l'autre voiture est plus jeune
                        elif oldest_passing_normal != None and self.hanging_normal_cars[i] != None and self.hanging_normal_cars[i].id < self.hanging_normal_cars[oldest_passing_normal].id and self.traffic_lights[i]:
                            oldest_passing_normal = i
                    # Si on a une voiture à faire passer
                    if oldest_passing_normal != None:
                        with self.lock_normal:
                            self.compteur_normal.value -= 1
                            self.normal_cars_per_road[oldest_passing_normal] -= 1
                            temp = self.normal_cars_per_road[oldest_passing_normal]
                        self.send_car_passed(self.hanging_normal_cars[oldest_passing_normal], temp)
                        self.hanging_normal_cars[oldest_passing_normal] = None
            time.sleep(static_time_scale * 0.8)
