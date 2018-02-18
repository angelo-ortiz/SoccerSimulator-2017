from soccersimulator import Strategy, SoccerAction
from .tools import StateFoot, get_random_strategy
from .conditions import must_intercept_gk, can_shoot, temps_interception
from .behaviour import shoot, beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, \
        dribbler, foncer, degager, aller_vers_balle, aller_dest, aller_vers_cage, intercepter_balle

## Strategie aleatoire
class RandomStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Random")
    def compute_strategy(self,state,id_team,id_player):
        return get_random_strategy()

## Strategie Fonceur
class FonceurStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Fonceur")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return foncer(me, beh_fonceur(me, "normal"))
        return aller_vers_balle(me)

## Strategie FonceurChallenge1
class FonceurChallenge1Strategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"FonceurChallenge1")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return foncer(me, beh_fonceur(me, "ch1"))
        return aller_vers_balle(me)

## Strategie Dribbler
class DribblerStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Dribbler")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return dribbler(me)
        return aller_vers_balle(me)

## Strategie Defendre
class GardienStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Gardien")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return degager(me)
        if must_intercept_gk(me):
            return intercepter_balle(me,temps_interception(me))
        return aller_vers_cage(me)

## Strategie Test
class TestStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Test")
    def compute_strategy(self,state,id_team,id_player):
        vect = Vector2D(GAME_WIDTH*0.1+GAME_HEIGHT/2.,GAME_HEIGHT/2.)
        me = StateFoot(state,id_team,id_player)
        if me.my_pos.x >= vect.x: 
            print("0")
            return SoccerAccion()
        print("1")
        return aller_dest(me, vect)
