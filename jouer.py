from ia.strategies import *

## Creation d'une equipe
pyteam = SoccerTeam(name="PyTeam")
thon = SoccerTeam(name="ThonTeam")
#pyteam.add("PyPlayer",GardienStrategy()) #Strategie qui ne fait rien
pyteam.add("PyPlayer",TestStrategy()) #Strategie qui ne fait rien
#pyteam.add("PyPlayer",FonceurStrategy()) #Strategie qui ne fait rien
#pyteam.add("DribbleurPyPlayer1",DribblerStrategy()) #Strategie qui ne fait rien
#pyteam.add("DribbleurPyPlayer2",GardienStrategy()) #Strategie qui ne fait rien

#thon.add("Gardien",GardienStrategy())   #Strategie qui ne fait rien
#thon.add("FoncCh1ThonPlayer2",FonceurChallenge1Strategy())   #Strategie qui ne fait rien
#thon.add("ThonPlayer",FonceurStrategy())   #Strategie aleatoire
#thon.add("DribbleurThonPlayer1",DribblerStrategy())   #Strategie qui ne fait rien
#thon.add("ThonPlayer",DribblerStrategy())   #Strategie qui ne fait rien

#Creation d'une partie
simu = Simulation(pyteam,thon)
#Jouer et afficher la partie
show_simu(simu)
