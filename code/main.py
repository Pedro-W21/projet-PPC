from multiprocessing import Process, Lock, Array, Value, Queue
import sysv_ipc
import normal
import priority
import lights
import coordinator
import sender
import sys

MQ_KEYS = [128, 256, 512, 1024]

if __name__ == "__main__":
    args_cons = sys.argv
    if len(args_cons) == 2:
        static_time_scale = float(args_cons[1])
        variable_time_scale = 2.0
    elif len(args_cons) == 3:
        static_time_scale = float(args_cons[1])
        variable_time_scale = float(args_cons[2])
    else:
        static_time_scale = 0.6
        variable_time_scale = 2.0

    # on ouvre, on ferme et on réouvre chaque MessageQueue au cas où elle soit déjà ouverte pour éviter les effets de bord
    for key in MQ_KEYS:        
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
        mq.remove()
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)

    sent_messages_queue = Queue(10000)
    chemin_prio_lock = Lock()
    chemin_prio_value = Value('i', 0, lock=False)
    static_time_scale_value = Value('f', static_time_scale, lock=False)
    static_time_scale_lock = Lock()
    variable_time_scale_value = Value('f', variable_time_scale, lock=False)
    variable_time_scale_lock = Lock()



    compteur_limiteur_normal = Value('i', 0, lock=False)
    lock_limiteur_normal = Lock()
    normal_cars_per_road = Array('i', 4, lock=False)

    normal_traffic_gen = normal.Normal(compteur_limiteur_normal, MQ_KEYS, lock_limiteur_normal, sent_messages_queue, static_time_scale_value, static_time_scale_lock, variable_time_scale_value, variable_time_scale_lock, normal_cars_per_road)
    normal_traffic_gen.start()

    compteur_limiteur_prio = Value('i', 0, lock=False)
    lock_limiteur_prio = Lock()
    prio_cars_per_road = Array('i', 4, lock=False)

    prio_traffic_gen = priority.Priority(compteur_limiteur_prio, MQ_KEYS, lock_limiteur_prio, sent_messages_queue, static_time_scale_value, static_time_scale_lock, variable_time_scale_value, variable_time_scale_lock, prio_cars_per_road)
    prio_traffic_gen.start()

    traffic_lights = Array('i', 4, lock=False)
    traffic_lights_lock = Lock()
    
    the_lights = lights.Lights(traffic_lights, traffic_lights_lock, MQ_KEYS, chemin_prio_lock, chemin_prio_value, static_time_scale_value, static_time_scale_lock, variable_time_scale_value, variable_time_scale_lock)
    the_lights.start()

    the_sender = sender.Sender(sent_messages_queue)
    the_sender.start()

    the_coordinator = coordinator.Coordinator(compteur_limiteur_normal, lock_limiteur_normal, compteur_limiteur_prio, lock_limiteur_prio, traffic_lights, traffic_lights_lock, MQ_KEYS, the_lights.pid, sent_messages_queue, chemin_prio_lock, chemin_prio_value, static_time_scale_value, static_time_scale_lock, variable_time_scale_value, variable_time_scale_lock, normal_cars_per_road, prio_cars_per_road)
    the_coordinator.start()


    normal_traffic_gen.join()
    prio_traffic_gen.join()
    the_lights.join()
    the_coordinator.join()
    the_sender.join()

    for key in MQ_KEYS:
        mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
        mq.remove()