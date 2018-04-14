# -*- coding: utf-8 -*-
from soccersimulator import Strategy
from .tools import StateFoot, get_random_strategy, is_in_radius_action
from .conditions import must_intercept, has_ball_control, is_defensive_zone, \
        is_close_goal, is_close_ball, opponent_approaches_my_goal, must_advance, free_teammate
from .behaviour import beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, \
    shoot, control, shiftAside, clear, clearSolo, goToBall, goToMyGoal, \
    tryInterception, interceptBall, fonceurCh1ApprochePower, shootPower, \
    power, goForwardsPA, goForwardsMF, cutDownAngle, pushUp, passBall, receiveBall
import pickle

def loadPath(fn):
    """
    Renvoie le chemin d'acces absolu du fichier
    passe en parametre pour la deserialisation
    d'un dictionnaire de parametres
    """
    from os.path import dirname, realpath, join
    return join(dirname(dirname(realpath(__file__))),"parameters",fn)



## Strategie Dribble + shoot
class DribbleShootStrategy(Strategy):
    def __init__(self, fn_st=None):
        Strategy.__init__(self,"DribbleShoot")
        with open(loadPath(fn_st),"rb") as f:
            self.dico = pickle.load(f)
        self.dico['distShoot'] = 36.
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return goForwardsPA(self, me, *self.args_dribble_pass_shoot())

## Strategie Controle + dribble
class ControlDribbleStrategy(Strategy):
    def __init__(self, fn_st=None):
        Strategy.__init__(self,"ControlDribble")
        with open(loadPath(fn_st),"rb") as f:
            self.dico = pickle.load(f)
        self.dico['distShoot'] = 36.
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'])
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'])
    def args_defense_loseMark(self):
        return (self.dico['decalX'], self.dico['decalY'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return goForwardsMF(me, *self.args_control_dribble_pass())
        if has_ball_control(me):
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA(self, me, *self.args_dribble_pass_shoot())
            return goForwardsMF(me, *self.args_control_dribble_pass())
        if is_defensive_zone(me, self.dico['distDefZone']):
            return shiftAside(me, *self.args_defense_loseMark())
        return goToBall(me)


class AttaquantStrategy(Strategy):
    def __init__(self,  fn_st=None):
        Strategy.__init__(self,"Attaquant")
        with open(loadPath(fn_st),"rb") as f:
            self.dico = pickle.load(f)
        self.dico['distShoot'] = 36.
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'])
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'])
    def args_defense_loseMark(self):
        return (self.dico['decalX'], self.dico['decalY'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA(self, me, *self.args_dribble_pass_shoot())
            return goForwardsMF(me, *self.args_control_dribble_pass())
        if is_defensive_zone(me, self.dico['distDefZone']):
            return shiftAside(me, *self.args_defense_loseMark())
        return goToBall(me)


## Strategie Revenir a la cage
class GoToMyGoalStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"GoToMyGoal")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return goToMyGoal(me)

## Strategie Monter
class PushUpStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"PushUp")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return pushUp(me)
    
## Strategie Passe
class PassStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Pass")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        tm = free_teammate(me, 30.)
        return passBall(me, tm, 4.5, 0.8)

## Strategie Reception d'une passe
class ReceivePassStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"ReceivePass")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        tm = free_teammate(me, 30.)
        return receiveBall(me, 0.7)

## Strategie Reduire l'angle de l'attaquant adverse
class CutDownAngleStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"CutDown")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return cutDownAngle(me, 40.)

## Strategie Marquer et essayer de recuperer la balle
class MarkStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Mark")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return clear(me, 40., 30., 3.7)
        return goToBall(me)


## Strategie Fonceur
"""
Le fonceur realise uniquement deux actions :
1/ il frappe la balle dès qu'il la controle
2/ il se deplace en ligne droite vers la balle
pour la recuperer
"""
class FonceurStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Fonceur")
        self.alpha = 0.2
        self.beta = 0.7
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return shoot(me, beh_fonceur(me, "normal"))
            #return shoot(me, shootPower(me, self.alpha, self.beta))
        return goToBall(me)
