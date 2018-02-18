from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from ia.strategies import *

## Creation d'une equipe
pyteam = SoccerTeam(name="Left")
thon = SoccerTeam(name="Right")
pyteam.add("GardienL",GardienStrategy()) #Strategie gardien/defenseur
#pyteam.add("FonceurL1",FonceurStrategy()) #Strategie fonceur
#pyteam.add("FonceurL2",FonceurStrategy()) #Strategie fonceur
#pyteam.add("DribbleurL1",DribblerStrategy()) #Strategie dribbleur
#pyteam.add("DribbleurL2",DribblerStrategy()) #Strategie dribbleur

#thon.add("GardienR",GardienStrategy())   #Strategie gardien/defenseur
thon.add("FonceurR1",FonceurStrategy())   #Strategie fonceur
#thon.add("FonceurR21",FonceurStrategy())   #Strategie fonceur
#thon.add("DribbleurR1",DribblerStrategy())   #Strategie dribbleur
#thon.add("DribbleurR2",DribblerStrategy())   #Strategie dribbleur

#Creation d'une partie
simu = Simulation(pyteam,thon)
#Jouer et afficher la partie
show_simu(simu)
