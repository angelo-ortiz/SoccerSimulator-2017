# -*- coding: utf-8 -*-
from soccersimulator import SoccerTeam, Simulation, Strategy
from soccersimulator import show_simu
from ia.strategies import *
import ia
import module3 as module
import module2 as module2
import module as module3

left = module.get_team(4)
#left = module3.get_team(4)
#right = module3.get_team(4)
right = ia.get_team(4)

simu = Simulation(right, left)
#simu = Simulation(left,right)
show_simu(simu)
