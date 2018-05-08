# -*- coding: utf-8 -*-
from soccersimulator import SoccerTeam, Simulation, Strategy
from soccersimulator import show_simu
from ia.strategies import *
import ia
import module
import module2
import module3
import module4
import module5
import module6
import module7

left = module3.get_team(4)
#left = module2.get_team(4)
#left = module3.get_team(4)
#left = module4.get_team(4)
#right = module3.get_team(4)
#right = ia.get_team(4)

myteam = SoccerTeam(name="ChPerFusion")
myteam.add("  3_Beckenbauer",CBNaif4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl",fn_st="4v4_st_dico_0508_1.pkl"))
myteam.add("  6_Matthaus", Gardien4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl",fn_st="4v4_st_dico_0508_1.pkl"))
myteam.add("  10_Pele", Attaquant4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl", fn_st="4v4_st_dico_0508_1.pkl"))
myteam.add("  9_Guerrero", Attaquant4v4Strategy(fn_gk="4v4_gk_dico_0508_1.pkl", fn_st="4v4_st_dico_0508_1.pkl"))

simu = Simulation(myteam, left)
#simu = Simulation(left,right)
show_simu(simu)
