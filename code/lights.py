import signal, time
from multiprocessing import Process
from math import sin


class Lights(Process):

    def __init__(self, lights_array, lights_array_lock, key_queues, chemin_priorite_lock, mqpriorite, static_time_scale, static_time_scale_lock, variable_time_scale, variable_time_scale_lock):
        super().__init__()
        self.traffic_lights = lights_array #array de 4 elements 0 ou 1
        self.keyQueues = key_queues #liste des key pour accéder aux 4 messageQueue/chemins
        self.lock = lights_array_lock
        self.lockprio = chemin_priorite_lock #lock pour la variable qui stocke le chemin d'où vient le véhicule prioritaire
        self.mqpriorite = mqpriorite #chemin d'où vient le véhicule prioritaire
        self.static_time_scale = static_time_scale
        self.static_time_scale_lock = static_time_scale_lock
        self.variable_time_scale = variable_time_scale
        self.variable_time_scale_lock = variable_time_scale_lock
        self.start_time = time.time()

    def handler(self,sig,frame):
        if sig == signal.SIGUSR1:
            #mettre tous les array à 0 sauf celui du chemin d'où vient la priorité
            with self.lockprio:
                for i in range(len(self.traffic_lights)):
                    if i == self.mqpriorite.value:
                        self.traffic_lights[i] = 1
                    else:
                        self.traffic_lights[i] = 0
                self.mqpriorite.value = 5
            while True:
                with self.lockprio:
                    if self.mqpriorite.value != 5:
                        self.mqpriorite.value = 7
                        break
            

    def run(self):
        signal.signal(signal.SIGUSR1, self.handler)
        #mode normal:
        while True:
            with self.static_time_scale_lock:
                static_time_scale = self.static_time_scale.value
            time.sleep(static_time_scale * 10.0)
            # print("TRAFFIC ALIVE")
            with self.lock:
                #vérifie si on est bien dans l'état normal et pas prioritaire, c'est-à-dire 2 feux verts pour 2 feux rouges et non 1 feu vert pour 3 feux rouges
                
                c = 0
                for j in self.traffic_lights:
                    if j == 1:
                        c += 1
                #si on est en mode priorité, change pour redevenir normal j 
                if c != 2:
                    self.traffic_lights[0] = 1
                    self.traffic_lights[1] = 0
                    self.traffic_lights[2] = 1
                    self.traffic_lights[3] = 0
                #puis on fait le négatif
                for i in range(len(self.traffic_lights)):
                    if i == 0:
                        self.traffic_lights[i] = 1
                    else:
                        self.traffic_lights[i] = 0
                

        
