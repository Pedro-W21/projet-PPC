# projet-PPC
repo de notre projet PPC de 3TC

## Exécution
- aller dans le répertoire `code`
- exécuter main.py avec un interpréteur python récent (testé sur 3.13 et 3.9) `python3 main.py` pour lancer la simulation
    - arguments optionnels possibles : l'échelle de temps statique et variable (en secondes)
    - l'échelle de temps statique sert dans le calcul du temps "minimum" entre 2 actions des process de simulation, 2 générations de voitures normales successives, 2 passages de voitures sur l'intersection, etc
    - l'échelle de temps variable sert dans le calcul d'une variation sinusoïdale du temps entre la génération de 2 voitures prioritaires et normales, pour créer des vagues d'affluence
    - ces 2 arguments sont des flottants positifs ou nuls à donner au programme : `python3 main.py {échelle de temps statique} {échelle de temps variable}` (Attention, les mettre à 0 teste la simulation à sa plus grande vitesse possible sur la machine cible, c'est trop rapide pour bien étudier ce qu'il se passe au Display !)
- pour lancer des clients qui regardent la simulation : `python3 display.py`, il n'y a pas de limite pratique à priori sur le nombre de clients possibles à part la capacité de la machine faisant fonctionner la simulation
- arrêter le Display ou la simulation se fait en arrêtant le programme

Remarque : à part `sysv_ipc` pour les MessageQueue, il n'y a pas de modules non-standards nécessaires à l'exécution