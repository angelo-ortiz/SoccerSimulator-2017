from .strategies import RandomStrategy, GardienStrategy, AttaquantStrategy
from .strategies import Fonceur1v1Strategy, FonceurChallenge1Strategy
from .strategies import Attaquant2v2Strategy, Gardien2v2Strategy, CBNaif2v2Strategy
from .strategies import Attaquant4v4Strategy, Gardien4v4Strategy, CBNaif4v4Strategy
from soccersimulator import SoccerTeam

def get_team(nb_players):
    myteam = SoccerTeam(name="ChPerFusion")
    if nb_players == 1:
        myteam.add("  9_Guerrero", Fonceur1v1Strategy(fn_gk="1v1_gk_dico_0505_1.pkl", fn_st="1v1_st_dico_0505_1.pkl"))
    if nb_players == 2:
        myteam.add("  10_Messi", Attaquant2v2Strategy(fn_gk="2v2_gk_dico_0508_2.pkl", fn_st="2v2_st_dico_0508_2.pkl"))
        myteam.add("  3_Beckenbauer", Gardien2v2Strategy(fn_gk="2v2_gk_dico_0508_2.pkl", fn_st="2v2_st_dico_0508_2.pkl"))
    if nb_players == 4:
        myteam.add("  3_Beckenbauer",CBNaif4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl",fn_st="4v4_st_dico_0508_1.pkl"))
        myteam.add("  6_Matthaus", Gardien4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl",fn_st="4v4_st_dico_0508_1.pkl"))
        myteam.add("  10_Pele", Attaquant4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl", fn_st="4v4_st_dico_0508_1.pkl"))
        myteam.add("  9_Guerrero", Attaquant4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl", fn_st="4v4_st_dico_0508_1.pkl"))
    return myteam

def get_team_challenge(num):
	myteam = SoccerTeam(name="ChPerFusion")
	if num == 1:
		myteam.add("  9_1v1_Chal "+str(num), FonceurChallenge1Strategy())
	return myteam
