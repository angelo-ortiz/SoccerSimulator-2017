# -*- coding: utf-8 -*-
from ia.ml_optimisation import LearningTeam
from ia.ml_strategies import Fonceur1v1Strategy

import module
import module2
import module3
import module4
import module5
import module6
import module7


opponentsList = [module2.get_team(1), module6.get_team(1), module3.get_team(1), module4.get_team(1), \
                 module5.get_team(1), module.get_team(1), module7.get_team(1)]
stratsList = [Fonceur1v1Strategy(fn_gk="1v1_gk_dico_0505_1.pkl", fn_st="1v1_st_dico_0505_1.pkl")]
MLTeam = LearningTeam(numPlayers=1, playerStrats=stratsList, oppList=opponentsList, numIter=30, numMatches=2, graphical=False) #t = 1120
# MLTeam = LearningTeam(numPlayers=1, playerStrats=stratsList, oppList=opponentsList[5:6], numIter=1, numMatches=1, graphical=True)
# MLTeam.initialize()
MLTeam.initialize(["ml_fon_0512_2.pkl", None, None, None])
MLTeam.start()
while MLTeam.next_match():
    MLTeam.start()
MLTeam.printQTableDebug(0)
MLTeam.save(["ml_fon_0512_2.pkl", None, None, None])
