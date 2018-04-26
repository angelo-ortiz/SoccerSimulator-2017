from .strategies import RandomStrategy, GardienStrategy, AttaquantStrategy
from .strategies import Fonceur1v1Strategy, FonceurChallenge1Strategy
from .strategies import Attaquant2v2Strategy, Gardien2v2Strategy, CBNaif2v2Strategy
from .strategies import Attaquant4v4Strategy, Gardien4v4Strategy, CBNaif4v4Strategy
from soccersimulator import SoccerTeam

def get_team(nb_players):
    myteam = SoccerTeam(name="ChPerFusion")
    if nb_players == 1:
        myteam.add("  9_Guerrero", Fonceur1v1Strategy(fn_gk="fonceur_gk_dico_0401.pkl", fn_st="fonceur_st_dico_0401.pkl"))
    if nb_players == 2:
        myteam.add("  10_Messi", Attaquant2v2Strategy(fn_gk="gk_dico_0425_2.pkl", fn_st="st_dico_0425_2.pkl"))
        myteam.add("  3_Beckenbauer", Gardien2v2Strategy(fn_gk="gk_dico_0425_2.pkl", fn_st="st_dico_0425_2.pkl"))
    if nb_players == 4:
        myteam.add("  3_Beckenbauer",CBNaif4v4Strategy(fn_gk="gk_dico_0325_p5_short.pkl",fn_st="st_dico_0325_p5_short.pkl"))
        myteam.add("  6_Matthaus", Gardien4v4Strategy(fn_gk="gk_dico_0325_p5_short.pkl",fn_st="st_dico_0325_p5_short.pkl"))
        #myteam.add("  6_Matthaus", Gardien4v4Strategy(fn_gk="gk_dico_0420_2.pkl", fn_st="st_dico_0420_2.pkl"))
        myteam.add("  10_Pele", Attaquant4v4Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
        #myteam.add("  10_Pele", Attaquant4v4Strategy(fn_gk="gk_dico_0420_2.pkl", fn_st="st_dico_0420_2.pkl"))
        #myteam.add("  9_Guerrero", Attaquant4v4Strategy(fn_gk="gk_dico_0420_2.pkl", fn_st="st_dico_0420_2.pkl"))
        myteam.add("  9_Guerrero", Attaquant4v4Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
    return myteam

def get_team_challenge(num):
	myteam = SoccerTeam(name="ChPerFusion")
	if num == 1:
		myteam.add("  9_Fonceur_Chal "+str(num),FonceurChallenge1Strategy())
	return myteam
