## AALpy

AALpy est une librairie Python permettant d'apprendre le fonctionnement de systèmes via plusieurs algorithmes.

Ce projet est un fork de la librairie AALpy implémentant un cas d'étude pour le mémoire ***Apprentissage d’automates avec abstraction de l’alphabet***.

Le wiki du projet originel peut être trouvé à l'adresse :
- <https://github.com/DES-Lab/AALpy/wiki>

Le fichier ***README*** du projet originel a été renommé ***OriginalAALpyREADME.md*** et le fichier ***Examples.py*** contient des exemples de fonctionnalités provenant de la librairie AALpy.

En revanche, les fichiers suivants sont propres au mémoire :
- ***DotFileGenerator.py***
- ***MqttExamples.py***
- ***TestMqtt.py***
- ***TestMqttPaho.py***
- ***TestMqttPub.py***
- ***TestMqttSub.py***

## Installation

La version minimum de Python requise est la 3.6.

Les modules nécessaires à l'exécution sont [pydot](https://pypi.org/project/pydot/), [scapy](https://pypi.org/project/scapy/) et [numpy](https://pypi.org/project/numpy/) (voir fichier ***requirements.txt***).

Il est nécessaire d'avoir installé [Graphviz](https://graphviz.org/) et de l'avoir ajouté au "path" afin de visualiser les modèles générés.

Le broker exploité dans cette expérimentation est le HiveMQ Community Edition (HiveMQ-ce) qui peut être lancé via [Docker](https://docs.docker.com/desktop/) en suivant les instructions présentes à l'adresse :
- https://github.com/hivemq/hivemq-community-edition?tab=readme-ov-file#run-with-docker

## Utilisation

Afin de lancer la procédure d'apprentissage, il suffit d'exécuter le fichier ***MqttExamples.py*** en ayant démarré l'image Docker du broker HiveMQ-ce au préalable.

Tous les paramètres d'apprentissage sont accessibles à partir du fichier ***MqttExamples.py***.

Dans la classe ***HiveMQ_Mapper*** :
- On peut modifier le nombre de clients (`clients`) au début du mapper.
- La valeur du timeout relatif aux PUBLISH se trouve dans la fonction ***is_publish_received***.
- La valeur du timeout relatif aux UNSUBSCRIBE se trouve dans la fonction ***send_unsubscribe***.

La valeur du paramètre `n_sampling`, le nombre de symboles d'entrée relatif aux tests de conformité (`num_steps`)
ainsi que la probabilité de démarrer une nouvelle séquence d'entrée durant les tests de conformité (`reset_prob`) sont tous les trois modifiables dans la fonction ***mqtt_real_example***.
