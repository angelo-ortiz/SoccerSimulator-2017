from soccersimulator import SoccerTeam, Simulation, Strategy
from soccersimulator import show_simu
from ia.strategies import *
from ia import *
import module
import module2
import module3
import module4
import module5

#left = module5.get_team(2)#Fonceur
#left = module.get_team(2)#BT
#left = module2.get_team(2)#Double def
left = module3.get_team(2)#Droite
#left = module4.get_team(2)#Double fonceur
right = get_team(2)
#right = module.get_team(2)#BT
"""
pyteam.add("  1L_GardienPrec", GardienPrecStrategy())
#pyteam.add("  9L_Fonceur", FonceurStrategy())
pyteam.add("  9L_AttPrec", AttaquantPrecStrategy())
#pyteam.add("TestAcc", TestAccStrategy(25.))

thon.add("  1R_Gardien", GardienStrategy())
thon.add("  7R_Attaquant", AttaquantStrategy())
#thon.add("  10R_Dribbler", DribblerStrategy())
#thon.add("Vide", Strategy())
"""
# 10 -> 12
# 15 -> 17
simu = Simulation(left, right)
#simu = Simulation(right, left)
show_simu(simu)
