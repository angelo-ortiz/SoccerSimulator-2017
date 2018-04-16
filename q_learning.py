# -*- coding: utf-8 -*-
from ia.machlearning_optimisation import LearningTeam
from ia.strategies_machlearning import Attaquant2v2Strategy, Defenseur2v2Strategy

import module
import module2
import module3
import module4
import module5
import module6
# import module7


opponentsList = [module.get_team(2), module2.get_team(2), module3.get_team(2), module4.get_team(2), \
                 module5.get_team(2), module6.get_team(2)]#, module7.get_team(2)]
stratsList = [Attaquant2v2Strategy(fn_gk="gk_dico_0407_3.pkl", fn_st="st_dico_0407_3.pkl"), \
              Defenseur2v2Strategy(fn_gk="gk_dico_0407_3.pkl", fn_st="st_dico_0407_3.pkl")]
MLTeam = LearningTeam(numPlayers=2, playerStrats=stratsList, oppList=opponentsList, numIter=5, numMatches=1, graphical=True)
#MLTeam.initialize()
MLTeam.initialize(["st_learning_0416_5.pkl", "gk_learning_0416_5.pkl", None, None])
MLTeam.start()
MLTeam.printQTableDebug(0)
MLTeam.save(["st_learning_0416_5.pkl", "gk_learning_0416_5.pkl", None, None])
