import random
from multiprocessing import Process


class Priority(Process):

    def __init__(self, compteur_normal, keyQueues, lock):
        super().__init__()
        self.compteur_normal = compteur_normal
        self.keyQueues = keyQueues
        self.lock = lock

    def normal_traffic_gen(self):
        #choisit de manière random où mettre une voiture
        depart = random.randint(0,3)
        arrivee = random.randint(0,3)
        #pour éviter que le chemin du départ soit l'arrivée
        while arrivee == depart :
            arrivee = random.randint(0,3)
        texte = f"{self.keyQueues[depart]}_{self.keyQueues[arrivee]}"
        mq.send(texte, type=1)
            