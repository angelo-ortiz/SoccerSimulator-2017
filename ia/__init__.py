from .strategies import RandomStrategy, FonceurStrategy, FonceurChallenge1Strategy, GardienStrategy
from .strategies import AttaquantStrategy
from soccersimulator import SoccerTeam

def get_team(nb_players):
    myteam = SoccerTeam(name="ChPerFusion")
    if nb_players == 1:
        myteam.add("  9_Fonceur", FonceurStrategy())
    if nb_players == 2:
        myteam.add("  7_Attaquant", AttaquantStrategy(fn_st="st_dico_FS7_OK.pkl"))
        myteam.add("  1_Goal", GardienStrategy(fn_gk="gk_dico_FS7_OK.pkl"))
    if nb_players == 4:
        myteam.add("Joueur 1",GardienStrategy())
        myteam.add("Joueur 2",RandomStrategy())
        myteam.add("Joueur 3",RandomStrategy())
        myteam.add("Joueur 4",RandomStrategy())
    return myteam	

def get_team_challenge(num):
	myteam = SoccerTeam(name="ChPerFusion")
	if num == 1:
		myteam.add("  9_Fonceur_Chal "+str(num),FonceurChallenge1Strategy())
	return myteam
