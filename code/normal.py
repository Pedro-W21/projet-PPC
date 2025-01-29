from multiprocessing import Process, Lock
import sysv_ipc
import random

class Normal(Process):

    def __init__(self, compteur_normal, keyQueues):
        super().__init__()
        self.compteur_normal = compteur_normal
        self.keyQueues = keyQueues

    def normal_traffic_gen(self):
        #choisit de manière random où mettre une voiture
        depart = random.randint(0,3)
        arrivee = random.randint(0,3)
        while arrivee == depart :
            arrivee = random.randint(0,3)
        texte = f"{self.keyQueues[depart]}_{self.keyQueues[arrivee]}"
        mq.send(texte, type=1)
            

