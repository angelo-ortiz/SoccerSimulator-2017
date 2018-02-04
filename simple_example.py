from soccersimulator import SoccerTeam, Simulation, show_simu, Strategy
from strategies  import RandomStrategy


## Creation d'une equipe
pyteam = SoccerTeam(name="PyTeam")
thon = SoccerTeam(name="ThonTeam")
pyteam.add("PyPlayer",Strategy()) #Strategie qui ne fait rien
thon.add("ThonPlayer",RandomStrategy())   #Strategie aleatoire

#Creation d'une partie
simu = Simulation(pyteam,thon)
#Jouer et afficher la partie
show_simu(simu)
