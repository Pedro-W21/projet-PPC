from multiprocessing import Process, Lock, Array, Value
import sysv_ipc
import normal
import priority
import lights
import coordinator

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

    prio_traffic_gen = priority.Priority(compteur_limiteur_prio, MQ_KEYS, lock_limiteur_prio)
    prio_traffic_gen.start()

    traffic_lights = Array('i', 4, lock=False)
    traffic_lights_lock = Lock()
    
    the_lights = lights.Lights(traffic_lights, traffic_lights_lock, MQ_KEYS)
    the_lights.start()

    the_coordinator = coordinator.Coordinator(compteur_limiteur_normal, lock_limiteur_normal, compteur_limiteur_prio, lock_limiteur_prio, traffic_lights, traffic_lights_lock, MQ_KEYS)
    the_coordinator.start()




    for key in MQ_KEYS:
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
        mq.remove()

    normal_traffic_gen.join()
    prio_traffic_gen.join()
    the_lights.join()
    the_coordinator.join()