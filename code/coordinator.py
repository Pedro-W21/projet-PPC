import random
from multiprocessing import Process, Queue
import sysv_ipc
import signal
import os
import time

PORT_COORD = 2000

class Car:
    def __init__(self, car_type, id, start, end):
        self.car_type = car_type
        self.id = id
        self.start = start
        self.end = end

def car_from_string(car_message, car_type) -> Car:
    split_message = car_message.split("_")
    return Car(car_type, int(split_message[0]), int(split_message[1]), int(split_message[2]))

class Coordinator(Process):

    def __init__(self, compteur_normal, lock_normal, compteur_prio, lock_prio, traffic_lights, traffic_lights_lock, keyQueues, traffic_lights_pid, sent_message_queue, chemin_priorite_lock, mqpriorite):
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


    def send_car_passed(self, car:Car):
        self.sent_messages_queue.put(f"PASSED {car.id} {car.start} {car.end} {car.car_type}")

    def run(self):
        while True:
            print(f"--------------------\n TICK COORD {self.tick}")
            self.tick += 1
            oldest_prio = None
            for i in range(4):
                if self.hanging_prio_cars[i] == None:
                    try:
                        car_message, ty = self.message_queues[i].receive(type=2, block=False)
                        self.hanging_prio_cars[i] = car_from_string(car_message.decode(), ty)
                        if oldest_prio == None:
                            oldest_prio = i
                        elif self.hanging_prio_cars[i].id < self.hanging_prio_cars[oldest_prio].id and self.hanging_prio_cars[i-1] == None:
                            oldest_prio = i
                         
                    except sysv_ipc.BusyError:
                        pass
                elif oldest_prio == None:
                    oldest_prio = i
                elif self.hanging_prio_cars[i] != None and self.hanging_prio_cars[i].id < self.hanging_prio_cars[oldest_prio].id and self.hanging_prio_cars[i-1] == None:
                    oldest_prio = i
                
            if oldest_prio != None:
                with self.lock_prio:
                    self.compteur_prio.value -= 1
                with self.chemin_prio_lock:
                    self.mq_priorite.value = oldest_prio
                # send signal to Lights
                os.kill(self.traffic_lights_pid, signal.SIGUSR1)
                #print(oldest_prio, self.hanging_prio_cars[oldest_prio].start)
                while True:
                    #with self.traffic_lights_lock:
                        print(self.traffic_lights[oldest_prio])
                        with self.chemin_prio_lock:
                            if self.mq_priorite.value == 5:
                                self.mq_priorite.value = 6
                                break
                        #print("IN TRAFFIC LIGHTS LOCK")
                        time.sleep(0.001)
                #time.sleep(1)
                while True:
                    #with self.traffic_lights_lock:
                        print(self.traffic_lights[oldest_prio])
                        with self.chemin_prio_lock:
                            if self.mq_priorite.value == 7:
                                break
                        #print("IN TRAFFIC LIGHTS LOCK")
                        time.sleep(0.001)
                self.send_car_passed(self.hanging_prio_cars[oldest_prio])
                self.hanging_prio_cars[oldest_prio] = None
            else:
                with self.traffic_lights_lock:
                    oldest_passing_normal = None
                    for i in range(4):
                        if self.hanging_normal_cars[i] == None:
                            try:
                                car_message, ty = self.message_queues[i].receive(type=1, block=False)
                                self.hanging_normal_cars[i] = car_from_string(car_message.decode(), ty)
                                if oldest_passing_normal == None and self.traffic_lights[i]:
                                    oldest_passing_normal = i
                                elif oldest_passing_normal != None and self.hanging_normal_cars[i].id < self.hanging_normal_cars[oldest_passing_normal].id and self.traffic_lights[i]:
                                    oldest_passing_normal = i
                            except sysv_ipc.BusyError:
                                pass
                        elif oldest_passing_normal == None and self.traffic_lights[i]:
                            oldest_passing_normal = i
                        elif oldest_passing_normal != None and self.hanging_normal_cars[i] != None and self.hanging_normal_cars[i].id < self.hanging_normal_cars[oldest_passing_normal].id and self.traffic_lights[i]:
                            oldest_passing_normal = i
                    #print(oldest_passing_normal)
                    if oldest_passing_normal != None:
                        with self.lock_normal:
                            self.compteur_normal.value -= 1
                        self.send_car_passed(self.hanging_normal_cars[oldest_passing_normal])
                        self.hanging_normal_cars[oldest_passing_normal] = None
            time.sleep(random.uniform(0.00001, 0.001))
