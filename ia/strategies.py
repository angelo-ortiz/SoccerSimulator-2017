from .tools import *
from .conditions import *
from .behaviour import *

## Strategie aleatoire
class RandomStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Random")
    def compute_strategy(self,state,id_team,id_player):
        return SoccerAction(Vector2D.create_random(-1.,1.),Vector2D.create_random(-1.,1.))

## Strategie Fonceur
class FonceurStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Fonceur")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if can_shoot(myState):
            return foncer(myState, beh_fonceur(myState, "normal"))
        return aller_vers_balle(myState)

## Strategie FonceurChallenge1
class FonceurChallenge1Strategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"FonceurChallenge1")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if can_shoot(myState):
            return foncer(myState, beh_fonceur(myState, "ch1"))
        return aller_vers_balle(myState)

## Strategie Dribbler
class DribblerStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Dribbler")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if can_shoot(myState):
            return dribbler(myState)
        return aller_vers_balle(myState)

## Strategie Defendre
class DefendreStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Defendre")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if can_shoot(myState):
            return degager(myState)
        if doit_intercepter(myState):
            return intercepter_balle(myState,temps_interception(myState))
        return aller_vers_cage(myState)
