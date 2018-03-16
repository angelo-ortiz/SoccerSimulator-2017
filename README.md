Sorbonne Université - Faculté des Sciences<br />
Département d'Informatique<br />
Unité d'enseignement 2I013 - Projet (application)<br />

Il s'agit du développement des joueurs participant à un jeu de foot.
Le code se trouve dans le module **ia**.<br />
Le fichier **tools.py** contient une classe enveloppe *Wrapper* et une classe *StateFoot* regroupant les informations concernant l'état du jeu à chaque instant et quelques fonctions utilitaires.<br />
Le fichier **strategies.py** comporte les diverses actions et les stratégies (ou super-actions) plausibles qui déterminent le comportement des joueurs sur le terrain. Quant à **strategy_optimisation.py**, on y retrouve les strategies à améliorer à l'aide de la recherche en grille.<br />
Le fichier **behaviour.py** regroupe les actions réalisées par nos joueurs.<br />
Le fichier **conditions.py** contient des méthodes qui dirigent la prise de décisions des joueurs.<br />
Le fichier **gs_optimisation.py** comporte les classes nécessaires pour la recherche en grille des paramètres de l'attaquant, le dribbleur et le gardien.<br />
Finalement, **gene_optimisation.py** contient la classe *dictParams* qui représente le dictionnaire de tous les paramètres à améliorer et la classe *GKStrikerTeam* qui précise les paramètres du gardien et de l'attaquant à prendre en compte par l'algorithme génétique.
