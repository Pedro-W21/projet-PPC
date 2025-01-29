from multiprocessing import Process, Lock, Array, Value
import sysv_ipc
import normal

MQ_KEYS = [128, 256, 512, 1024]

if __name__ == "__main__":
    for key in MQ_KEYS:        
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

    compteur_limiteur_normal = Value('i', 0, lock=False)
    lock_limiteur_normal = Lock()

    normal_traffic_gen = normal.Normal(compteur_limiteur_normal, MQ_KEYS, lock_limiteur_normal)
    normal_traffic_gen.start()

    compteur_limiteur_prio = Value('i', 0, lock=False)
    lock_limiteur_prio = Lock()

    traffic_lights = Array('i', 4, lock=False)
    traffic_lights_lock = Lock()





    for key in MQ_KEYS:
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
        mq.remove()