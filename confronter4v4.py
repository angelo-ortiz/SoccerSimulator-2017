from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from ia.gene_optimisation import setCounters, setCountersSolo, dictParams, FullTeam
import ia
import module
import module2
import module3
import module5
import module6
import random

size = 10
nbIter = 8
nbMatch = 2
nVect = 3
full_team = FullTeam(size=size)
full_team.start()
right = [module.get_team(4), module2.get_team(4), module3.get_team(4), \
         module6.get_team(4), module5.get_team(4)]
for n in range(nbIter):
    full_team.restart()
    for i in range(size):
        ft = full_team.getTeam(i)
        ft_p = full_team.getVector(i)
        for opp in right:
            for j in range(nbMatch):
                rev = False
                simu = Simulation(ft,opp)
                simu.start()
                setCountersSolo(simu, ft_p, rev)
            for j in range(nbMatch):
                rev = True
                simu = Simulation(opp, ft)
                simu.start()
                setCountersSolo(simu, ft_p, rev)
    print(n)
    full_team.update()

full_team.printVectors(nVect)
full_team.save(["4v4_gk_dico_0508_1.pkl", "4v4_st_dico_0508_1.pkl"])
simu = Simulation(full_team.getBestTeam(),right[0])
show_simu(simu)
