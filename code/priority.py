from multiprocessing import Process, Lock
import sysv_ipc
import random

class Priority(Process):

    def __init__(self, compteur_global, keyQueues, lock_compteur_global):
        super().__init__()
        self.keyQueues = keyQueues
        self.lock_compteur_normal = lock_compteur_global
        self.compteur_global = compteur_global #compteur global de nombre de voitures prioritaires
        self.id = 0

    def run(self):
        while True:
            #on regarde une première fois le compteur global
            with self.lock_compteur_global:
                    compteur_temporaire = self.compteur_global
            #boucle principale
            if compteur_temporaire <= 20:
                #choisit de manière random où mettre une voiture
                depart = random.randint(0,3)
                arrivee = random.randint(0,3)
                #pour éviter que le chemin du départ soit l'arrivée
                while arrivee == depart :
                    arrivee = random.randint(0,3)
                texte = f"{self.id}_{self.keyQueues[depart]}_{self.keyQueues[arrivee]}"
                mq = sysv_ipc.MessageQueue(self.keyQueues[depart])
                mq.send(texte, type=2)
                with self.lock_compteur_global:
                    self.compteur_global += 1
                    compteur_temporaire = self.compteur_global
                self.id += 1
