from soccersimulator import Strategy
from .tools import StateFoot, get_random_strategy, get_empty_strategy
from .conditions import must_intercept_gk, can_shoot, temps_interception, is_in_box, is_defense_zone, is_close_goal, is_close_ball
from .behaviour import shoot, beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, dribbler, decaler,\
        foncer, degager, degager_solo, aller_vers_balle, aller_vers_cage, intercepter_balle, \
        fonceurCh1ApprochePower, force, power

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
        self.alpha = 0.2
        self.beta = 0.7
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return foncer(me, beh_fonceur(me, "normal"))
            #return foncer(me, force(me, self.alpha, self.beta))
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
        self.alpha = 0.2
        self.beta = 0.7
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            if is_close_goal(me):
                return foncer(me, force(me, self.alpha, self.beta))
            return dribbler(me, power(me))
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
            return dribbler(me, power(me))
        return aller_vers_balle(me)

## Strategie Gardien
class GardienStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Gardien")
        self.temps = 6
        self.n = 6
        self.distance = 15.
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            self.n = self.temps - 1
            return degager_solo(me)
        if must_intercept_gk(me, self.distance):
            self.n -= 1
            print(self.n)
            if self.n <= 0 :
                self.n = self.temps - 1
                return get_empty_strategy()
            return intercepter_balle(me,self.n)
        return aller_vers_cage(me)

## Strategie Gardien
class GardienPrecStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Gardien")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return degager_solo(me)
        if must_intercept_gk(me):
            return intercepter_balle(me,10.)
        return aller_vers_cage(me)
