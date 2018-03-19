from soccersimulator import SoccerTeam, Simulation, Strategy
from soccersimulator import show_simu
from ia.strategies import *
from ia import *
import module
import module2
import module3
import module4
import module5
import module6

#left = module5.get_team(2)#Fonceur
#left = module.get_team(2)#BT
#left = module2.get_team(2)#Double def
#left = module3.get_team(2)#Droite
#left = module4.get_team(2)#Double fonceur
left = module6.get_team(2)#BT2
right = get_team(2)
#right = module.get_team(2)#BT

#simu = Simulation(left, right)
simu = Simulation(right, left)
show_simu(simu)
