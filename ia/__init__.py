from .strategies import RandomStrategy, FonceurStrategy, GardienStrategy, FonceurModifStrategy#, FonceurChallenge1Strategy
from .strategies import AttaquantStrategy, AttaquantModifStrategy, GardienModifStrategy, CBNaifStrategy, CBNaif2v2Strategy
from .strategies import AttaquantModif2v2Strategy, GardienModif2v2Strategy
from soccersimulator import SoccerTeam

def get_team(nb_players):
    myteam = SoccerTeam(name="ChPerFusion")
    if nb_players == 1:
        myteam.add("  9_Fonceur", FonceurModifStrategy(fn_gk="fonceur_gk_dico_0401.pkl", fn_st="fonceur_st_dico_0401.pkl"))
    if nb_players == 2:
        myteam.add("  7_Attaquant", AttaquantModif2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
        myteam.add("  1_Goal", GardienModif2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl",fn_st="st_dico_0325_p5_short.pkl"))
        #myteam.add("  3_CBNaif",CBNaif2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl",fn_st="st_dico_0325_p5_short.pkl"))
    if nb_players == 4:
        myteam.add("  3_CBNaif",CBNaifStrategy(fn_gk="gk_dico_0325_p5_short.pkl",fn_st="st_dico_0325_p5_short.pkl"))
        myteam.add("  1_Goal", GardienModifStrategy(fn_gk="gk_dico_0325_p5_short.pkl",fn_st="st_dico_0325_p5_short.pkl"))
        myteam.add("  7_Attaquant", AttaquantModifStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
        myteam.add("  9_Attaquant", AttaquantModifStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
    return myteam

def get_team_challenge(num):
	myteam = SoccerTeam(name="ChPerFusion")
	if num == 1:
		#myteam.add("  9_Fonceur_Chal "+str(num),FonceurChallenge1Strategy())
		myteam.add("  9_Fonceur_Chal "+str(num),RandomStrategy())
	return myteam
