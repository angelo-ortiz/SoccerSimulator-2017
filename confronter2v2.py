from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from ia.gene_optimisation import setCounters, setCountersSolo, dictParams, GKStrikerTeam
import ia
import module
import module2
import module3
import module4
import module5
import module6
import module7

size = 12
nbIter = 15
nbMatch = 2
nVect = 3
gk_st_team = GKStrikerTeam(size=size)
gk_st_team.start()
right = [module.get_team(2), module2.get_team(2), module3.get_team(2), module6.get_team(2), module4.get_team(2), module7.get_team(2), module5.get_team(2)]
for n in range(nbIter):
    gk_st_team.restart()
    for i in range(size):
        gk_st = gk_st_team.getTeam(i)
        gk_st_p = gk_st_team.getVector(i)
        for opp in right:
            for j in range(nbMatch):
                rev = False
                simu = Simulation(gk_st,opp)
                simu.start()
                setCountersSolo(simu, gk_st_p, rev)
            for j in range(nbMatch):
                rev = True
                simu = Simulation(opp, gk_st)
                simu.start()
                setCountersSolo(simu, gk_st_p, rev)
    print(n)
    gk_st_team.update()

gk_st_team.printVectors(nVect)
gk_st_team.save(["2v2_gk_dico_0508_2.pkl", "2v2_st_dico_0508_2.pkl"])
simu = Simulation(gk_st_team.getBestTeam(),right[0])
show_simu(simu)
