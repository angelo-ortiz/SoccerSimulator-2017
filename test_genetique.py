from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from ia.strategies import *

gk_st_team = GKStrikerTeam()
gk_cf_team = GKCForwardTeam()
for i in range(10000):
    lteam = gk_st_team.get_team(j)
    rteam = gk_cf_team.get_team(k)
    simu = Simulation(lteam,rteam)
   # TODO
   """
    1/ lancer d'abord les size*size matches (10*10 ?)
    2/ reprendre les x meilleurs resultats (25% ?)
    3/ relancer y tests de plus (???) ou le faire jusqu'a ce 
    que l'optimisation soit bonne (toujours des matches nuls)

   """



#show_simu(simu)
