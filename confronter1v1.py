from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from ia.gene_optimisation import setCounters, setCountersSolo, dictParams, STTeam
import ia
import module
import module2
import module3
import module4
import module5
import module6
import module7
import random

size = 12
nbIter = 15
nbMatch = 2
nVect = 3
st_team = STTeam(size=size)
st_team.start()
right = [module.get_team(1), module7.get_team(1), module2.get_team(1), module3.get_team(1), module5.get_team(1), module6.get_team(1), module4.get_team(1)]
for n in range(nbIter):
    st_team.restart()
    for i in range(size):
        st = st_team.getTeam(i)
        st_p = st_team.getVector(i)
        for opp in right:
            for j in range(nbMatch):
                rev = False
                simu = Simulation(st,opp)
                simu.start()
                setCountersSolo(simu, st_p, rev)
            for j in range(nbMatch):
                rev = True
                simu = Simulation(opp, st)
                simu.start()
                setCountersSolo(simu, st_p, rev)
    print(n)
    st_team.update()

st_team.printVectors(nVect)
st_team.save(["1v1_gk_dico_0512_1.pkl", "1v1_st_dico_0512_1.pkl"])
simu = Simulation(st_team.getBestTeam(),right[0])
show_simu(simu)
