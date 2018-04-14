# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from soccersimulator import SoccerTeam, Simulation, show_simu
from ia.machlearning_optimisation import LearningTeam
from ia.gene_optimisation import savePath
import numpy as np

import module
import module2
import module3
import module4
import module5
import module6
import module7


def initializeMatrix():
    """
    s : number of states
    a : number of actions/strategies
    Q : matrix of rewards
    """
    s = 100
    a = 5
    Q = [] * s
    return Q


def initializeState():
    """
    """
    S = None
    return S

def isTerminal(state):
    """
    """
    return False


Q = initializeMatrix()
opponentsList = [module.get_team(2), module2.get_team(2), module3.get_team(2), module4.get_team(2), \
                 module5.get_team(2), module6.get_team(2), module7.get_team(2)]
MLTeam = LearningTeam(Q)
S = initializeState()
nbIter = 10
nbMatches = 3
for n in range(nbIter):
    for opp in opponentsList:
        for j in range(nbMatches): # left side
            simu = Simulation(gk_st,opp)
            simu.start()
            MLTeam.compute_rewards()
        for j in range(nbMatches): # right side
            simu = Simulation(opp, gk_st)
            simu.start()
            MLTeam.compute_rewards()
    print(n)
MLTeam.save("learning_0410_1.pkl")
simu = Simulation(MLTeam.finalTeam(),right[0])
show_simu(simu)
