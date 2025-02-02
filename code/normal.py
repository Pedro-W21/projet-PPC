from multiprocessing import Process, Lock
import sysv_ipc
import random
import time

class Normal(Process):

    def __init__(self, compteur_global, keyQueues, lock_compteur_global, sent_messages_queue):
        super().__init__()
        self.keyQueues = keyQueues
        self.lock_compteur_global = lock_compteur_global
        self.compteur_global = compteur_global #compteur global de nombre de voitures normales
        self.id = 0
        self.messageQueues = [sysv_ipc.MessageQueue(key) for key in keyQueues]
        self.sent_messages_queue = sent_messages_queue

    def run(self):
        while True:
            #on regarde une première fois le compteur global
            with self.lock_compteur_global:
                    compteur_temporaire = self.compteur_global.value
            #boucle principale
            if compteur_temporaire <= 100:

                #print(f"NORMAL AT {compteur_temporaire}")
                #choisit de manière random où mettre une voiture
                depart = random.randint(0,3)
                arrivee = random.randint(0,3)
                #pour éviter que le chemin du départ soit l'arrivée
                while arrivee == depart :
                    arrivee = random.randint(0,3)
                texte = f"{self.id}_{depart}_{arrivee}"
                #print("adding normal", texte)
                mq = self.messageQueues[depart]
                mq.send(texte.encode(), type=1)
                self.sent_messages_queue.put(f"NEW {self.id} {depart} {arrivee} 1 {compteur_temporaire}")
                with self.lock_compteur_global:
                    self.compteur_global.value += 1
                    compteur_temporaire = self.compteur_global.value
                self.id += 1
            time.sleep(random.uniform(0.0001, 0.003))