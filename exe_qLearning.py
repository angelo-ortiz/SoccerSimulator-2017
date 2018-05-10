# -*- coding: utf-8 -*-
from ia.ml_optimisation import LearningTeam
from ia.ml_strategies import Attaquant2v2Strategy, Defenseur2v2Strategy

import module
import module2
import module3
import module4
import module5
import module6
import module7


opponentsList = [module.get_team(2), module2.get_team(2), module3.get_team(2), module4.get_team(2), \
                 module5.get_team(2), module6.get_team(2), module7.get_team(2)]
stratsList = [Attaquant2v2Strategy(fn_gk="2v2_gk_dico_0428_1.pkl", fn_st="2v2_st_dico_0428_1.pkl"), \
              Defenseur2v2Strategy(fn_gk="2v2_gk_dico_0428_1.pkl", fn_st="2v2_st_dico_0428_1.pkl")]
# MLTeam = LearningTeam(numPlayers=2, playerStrats=stratsList, oppList=opponentsList, numIter=30, numMatches=2, graphical=False)
MLTeam = LearningTeam(numPlayers=2, playerStrats=stratsList, oppList=opponentsList[:1], numIter=1, numMatches=1, graphical=True)
# MLTeam.initialize()
MLTeam.initialize(["ml_st_0510_1.pkl", "ml_gk_0510_1.pkl", None, None])
MLTeam.start()
while MLTeam.next_match():
    MLTeam.start()
MLTeam.printQTableDebug(0)
# MLTeam.save(["ml_st_0510_1.pkl", "ml_gk_0510_1.pkl", None, None])
