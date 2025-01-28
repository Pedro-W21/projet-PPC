# Les Process

## normal_traffic_gen

- a les 4 MessageQueue **globales** et un compteur de voitures non-prioritaires **global**
- choisit la queue où mettre une voiture de façon aléatoire (en prenant en compte le nombre de voiture par Queue/total)
- choisit la destination en prenant la soustraction du set des messagesqueues - la queue de départ
- lock le compteur
    - rajoute la voiture dans la message queue qu'il faut, type = 1

## priority_traffic_gen

- a les 4 MessageQueue **globales** et le compteur de voitures prioritaires **global** et une messageQueue d'index de route contenant du traffic prioritaire
- choisit queue de départ et de destination pour son traffic en priorité
- lock le compteur de voitures prioritaires
    - rajoute la voiture dans la message queue qu'il faut, type = 2
    - rajoute la messagequeue choisie dans la messagequeue du traffic prioritaire
    - envoie un signal à Lights 
- **QUE UN SEUL PRIORITY A LA FOIS A PRIORI**

## coordinator

- a les 4 messageQueue **globales**, la messageQueue de priorité, et les compteurs de voitures, et l'array des traffic lights, ainsi qu'un stockage local de voitures "en cours de calcul"
- par itération :
    - ordre de priorité des voitures :
        - essaie de get la messageQueue de priorité
        - regarde les routes encore ouvertes qui n'ont pas de voiture "en cours de calcul"
        - regarde les voitures "en cours de calcul" des routes ouvertes
    - pour rediriger chaque voiture :
        - acquérir le lock
        - si elle tourne à droite, on la met sur la bonne MessageQueue directement
        - si elle va tout droit
            - si prioritaire
                - on met dans la bonne MessageQueue directement
            - sinon
                - on met dans les voitures "en cours de calcul"

## Lights

- a un array partagé de 4 feux, un lock sur les feux, et gère les signaux système
- en "normal mode", inverse les états des signaux toutes les N secondes
- lorsqu'il reçoit un signal, le handler prend l'argument de la route source avec le signal et met en rouge le reste


## display 
- sockets from normal_traffic_gen, priority_traffic_gen, coordinator, and lights
    - le display s'y connecte et reçoit les infos, ne parle pas dans l'autre sens
- get chaque nouvelle voiture de normal_traffic_gen et les voitures prioritaires de priority_traffic_gen
- get les voitures qui passent et sous quelles conditions de coordinator
- get les changements de feux de lights
- affiche le tout 
    - proposition d'affichage :


## messages dans les MessageQueue de routes
- "{route_destination}", pas d'autre information est nécessaire à priori (avec le type des messages)
- 