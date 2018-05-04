Sorbonne Université - Faculté des Sciences<br />
Département d'Informatique<br />
Unité d'enseignement 2I013 - Projet (application)<br />

Il s'agit du développement des joueurs participant à un jeu de foot.
Le code se trouve dans le module **ia**.<br />
Le fichier **tools** contient une classe enveloppe *Wrapper* et une classe *StateFoot* regroupant les informations concernant l'état du jeu à chaque instant et quelques fonctions utilitaires.<br />
Le fichier **strategies** comporte les diverses actions et les stratégies (ou super-actions) réalisables qui déterminent le comportement des joueurs sur le terrain. Les préfixes *dt*, *gs* et *ml* indiquent l'usage particulier pour certaines stratégies, en l'occurrence pour les arbres de décision, la recherche en grille et un algorithme d'apprentissage automatique.<br />
Le fichier **actions** regroupe les actions réalisées par nos joueurs et **behaviour** comporte les super-actions, i.e. des regroupements d'actions pour des multiples phases du jeu.<br />
Le fichier **conditions** contient des méthodes qui dirigent la prise de décisions des joueurs.<br />
Les fichiers **optimisation** comportent les classes nécessaires pour la recherche en grille (gs), l'implémentation d'un algorithme génétique (gene) et la mise en œuvre d'un algorithme d'apprentissage automatique.<br />
