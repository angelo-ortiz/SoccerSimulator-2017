from soccersimulator import Strategy, SoccerAction
from .tools import StateFoot, get_random_strategy
from .conditions import must_intercept_gk, can_shoot, temps_interception, is_in_box, is_defense_zone
from .behaviour import shoot, beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, dribbler, decaler,\
        foncer, degager, aller_vers_balle, aller_dest, aller_vers_cage, intercepter_balle, \
        fonceurCh1ApprochePower, force

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

## Strategie Attaquant
class AttaquantStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Attaquant")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return foncer(me, beh_fonceur(me, "ch1"))
        if is_defense_zone(me):
            return decaler(me)
        return aller_vers_balle(me)

## Strategie Dribbler
class DribblerStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Dribbler")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            if is_in_box(me):
                return foncer(me, fonceurCh1ApprochePower)
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

class ShootTestStrategy(Strategy):
    def __init__(self, dist=None, alpha=None, beta=None):
        Strategy.__init__(self,"Shoot")
        self.dist = dist
        self.alpha = alpha
        self.beta = beta
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return foncer(me, force(me, self.alpha, self.beta))



