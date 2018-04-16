# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from soccersimulator import SoccerTeam, Simulation, show_simu
from ia.machlearning_optimisation import LearningTeam
from ia.strategies_machlearning import Attaquant2v2Strategy, Defenseur2v2Strategy
import numpy as np

import module
import module2
import module3
import module4
import module5
import module6
import module7


opponentsList = [module.get_team(2), module2.get_team(2), module3.get_team(2), module4.get_team(2), \
                 module5.get_team(2), module6.get_team(2), module7.get_team(2)]
stratsList = [Attaquant2v2Strategy(fn_gk="gk_dico_0407_3.pkl", fn_st="st_dico_0407_3.pkl"), \
              Defenseur2v2Strategy(fn_gk="gk_dico_0407_3.pkl", fn_st="st_dico_0407_3.pkl")]
MLTeam = LearningTeam(numPlayers=2, playerStrats=stratsList, oppList=opponentsList, numIter=3, numMatches=1, graphical=False)
MLTeam.initialize()
#MLTeam.initialize(["st_learning_0416_4.pkl", "gk_learning_0416_4.pkl", None, None])
MLTeam.start()
MLTeam.printQTableDebug(0)
MLTeam.save(["st_learning_0416_4.pkl", "gk_learning_0416_4.pkl", None, None])
