from soccersimulator import ChallengeFonceurButeur, SoccerTeam,show_simu
from strategies import RandomStrategy, FonceurStrategy

team = SoccerTeam("FonceurEquipe")
team.add("FonceurJoueur",FonceurStrategy())

challenge = ChallengeFonceurButeur(team,max_but=20)
show_simu(challenge)
print("temps moyen : ",challenge.stats_score, "\nliste des temps",challenge.resultats)
