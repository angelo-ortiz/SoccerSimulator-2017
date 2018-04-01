# -*- coding: utf-8 -*-
from soccersimulator import SoccerTeam, Simulation, Strategy
from soccersimulator import show_simu
from ia.strategies import *
import ia
import module as module
import module2 as module2
import module7 as module3

#left = module.get_team(4)
left = module3.get_team(4)
#right = module3.get_team(4)
right = ia.get_team(4)
naif = SoccerTeam(name="Naif")
charge = SoccerTeam(name="Charge")
charge.add("   GK", GardienModifStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
charge.add("   ST", AttaquantModifStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
naif.add("   ST", AttaquantModifStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
naif.add("   CBNaif", CBNaifStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
#naif.add("   Fonceur", FonceurStrategy())

#simu = Simulation(left,naif)
#simu = Simulation(charge,naif)
#simu = Simulation(left,charge)
#simu = Simulation(right, left)
simu = Simulation(left,right)
#simu = Simulation(right,naif)
show_simu(simu)
