from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from ia.gene_optimisation import setCounters, dictParams, GKStrikerTeam#, GKCForwardTeam
import random

size = 10#50
nbIter = 15#500
nVect = 5
gk_st_team = GKStrikerTeam(size=size)
gk_st_team.start()
gk_cf_team = GKStrikerTeam(size=size) #GKCForwardTeam(size)
gk_cf_team.start()
for n in range(nbIter):
    gk_st_team.restart()
    gk_cf_team.restart()
    for i in range(size):
        gk_st = gk_st_team.getTeam(i)
        gk_st_p = gk_st_team.getVector(i)
        for j in range(size):
            gk_cf = gk_cf_team.getTeam(j)
            gk_cf_p = gk_cf_team.getVector(j)
            team = {1: (gk_st, gk_st_p), 2:(gk_cf, gk_cf_p)}
            if random.random() < 0.5:
                team[1], team[2] = team[2], team[1]
            simu = Simulation(team[1][0],team[2][0])
            simu.start()
            #print(j)
            setCounters(simu, team[1][1], team[2][1])
    print(n)
    gk_st_team.update()
    gk_cf_team.update()

gk_st_team.printVectors(nVect)
gk_cf_team.printVectors(nVect)
gk_st_team.save()
simu = Simulation(gk_st_team.getBestTeam(),gk_cf_team.getBestTeam())
show_simu(simu)
