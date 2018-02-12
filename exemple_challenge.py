from soccersimulator import ChallengeFonceurButeur, SoccerTeam,show_simu
from ia.strategies import FonceurChallenge1Strategy

team = SoccerTeam("ChPerFusion")
team.add("FonceurCh1Joueur",FonceurChallenge1Strategy())

challenge = ChallengeFonceurButeur(team,max_but=20)
show_simu(challenge)
print("temps moyen : ",challenge.stats_score, "\nliste des temps",challenge.resultats)
