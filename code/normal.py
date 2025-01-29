from multiprocessing import Process, Lock
import sysv_ipc
import random

class Normal(Process):

    def __init__(self, compteur_normal, queueN, queueS, queueO, queueE):
        super().__init__()
        self.compteur_normal = compteur_normal
        self.queueN = queueN
        self.queueS = queueS
        self.queueO = queueO
        self.queueE = queueE

    def normal_traffic_gen(self):
        #choisit de manière random où mettre une voiture
        chemin = ['queueN','queueS','queueO','queueE']
        depart = random.randint(0,3)
        arrivee = random.randint(0,3)
        while arrivee == depart :
            arrivee = random.randint(0,3)
        texte = f"{chemin[depart]}_{chemin[arrivee]}"
        mq.send(texte, type=1)
            

