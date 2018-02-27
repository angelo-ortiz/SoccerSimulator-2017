from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from ia.opt_generique import setCounters, dictParams, GKStrikerTeam, GKCForwardTeam

size = 30
nbIter = 1000
gk_st_team = GKStrikerTeam(size)
gk_st_team.random()
gk_cf_team = GKCForwardTeam(size)
gk_cf_team.random()
for i in range(nbIter):
    gk_st_team.restart()
    gk_cf_team.restart()
    for i in range(size):
        gk_st = gk_st_team.getTeam(i)
        gk_st_p = gk_st_team.getVector(i)
        for j in range(size):
            gk_cf = gk_cf_team.getTeam(j)
            gk_cf_p = gk_cf_team.getVector(j)
            team = {1: (gk_st, gk_st_p), 2:(gk_cf, gk_cf_p)}
            if random.random() < 0.5: # Pour la moitie des matches, on change la position des equipes
                team[1], team[2] = team[2], team[1]
            simu = Simulation(team[1][0],team[2][0])
            setCounters(simu, team[1][1], team[2][1])

#show_simu(simu)
