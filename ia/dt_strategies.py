# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from .tools import StateFoot, get_random_strategy, is_in_radius_action, nearest_defender
from .conditions import must_intercept, has_ball_control, is_defensive_zone, \
        is_close_goal, is_close_ball, opponent_approaches_my_goal, must_advance, \
        free_teammate, had_ball_control, is_kick_off
from .behaviour import beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, \
    shoot, control, shiftAside, clear, clearSolo, goToBall, goToMyGoal, \
    tryInterception, interceptBall, fonceurCh1ApprochePower, shootPower, \
    power, goForwardsPA, goForwardsMF, cutDownAngle, pushUp, passBall, \
    passiveSituation, kickAt, \
    cutDownAngle_gk, dribble
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
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"DribbleShoot")
        with open(loadPath(fn_st),"rb") as f:
            self.dico = pickle.load(f)
        with open(loadPath(fn_gk),"rb") as f:
            self.dico.update(pickle.load(f))
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 23.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'], \
                self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['rayPressing'], \
                self.dico['distPasse'], self.dico['angleInter'], self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return goForwardsPA(me, *self.args_dribble_pass_shoot())
        return goToBall(me)

## Strategie Controle + dribble
class ControlDribbleStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"ControlDribble")
        with open(loadPath(fn_st),"rb") as f:
            self.dico = pickle.load(f)
        with open(loadPath(fn_gk),"rb") as f:
            self.dico.update(pickle.load(f))
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 23.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'], self.dico['powerPasse'], \
                self.dico['thetaPasse'], self.dico['rayPressing'], self.dico['distPasse'], \
                self.dico['angleInter'], self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return goForwardsMF(me, *self.args_control_dribble_pass())
        return goToBall(me)


class AttaquantStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Attaquant")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 23.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'], \
                self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['rayPressing'], \
                self.dico['distPasse'], self.dico['angleInter'], self.dico['coeffPushUp'])
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'], self.dico['powerPasse'], \
                self.dico['thetaPasse'], self.dico['rayPressing'], self.dico['distPasse'], \
                self.dico['angleInter'], self.dico['coeffPushUp'])
    def args_receivePass_loseMark(self):
        return (self.dico['decalX'], self.dico['decalY'], self.dico['rayRecept'], \
                self.dico['angleRecept'], self.dico['rayReprise'], self.dico['angleReprise'], \
                self.dico['distMontee'], self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if is_kick_off(me):
            if has_ball_control(me):
                return kickAt(me, Vector2D(me.opp_goal.x, 100.),6.)
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA(me, *self.args_dribble_pass_shoot())
            return goForwardsMF(me, *self.args_control_dribble_pass())
        return passiveSituation(me, self.dico, *self.args_receivePass_loseMark())

class DefenseStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Defense")
        if fn_gk is not None:
            with open(loadPath(fn_gk),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_st),"rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 23.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'], \
                self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['rayPressing'], \
                self.dico['distPasse'], self.dico['angleInter'], self.dico['coeffPushUp'])
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'], self.dico['powerPasse'], \
                self.dico['thetaPasse'], self.dico['rayPressing'], self.dico['distPasse'], \
                self.dico['angleInter'], self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if is_kick_off(me):
            if has_ball_control(me):
                return shoot(me,6.)
            return goToBall(me)
        if me.is_nearest_ball():
            return tryInterception(me, self.dico)
            #return goToBall(me)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return goToMyGoal(me)
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        return cutDownAngle_gk(me, self.dico['distMontee'])


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
        if has_ball_control(me) and tm is not None:
            return passBall(me, tm, 4.5, 0.8)
        return goToBall(me)

## Strategie Reception d'une passe
class PassiveSituationStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"PassiveSituation")
        with open(loadPath(fn_st),"rb") as f:
            self.dico = pickle.load(f)
        with open(loadPath(fn_gk),"rb") as f:
            self.dico.update(pickle.load(f))
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 23.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
    def args_receivePass_loseMark(self):
        return (self.dico['decalX'], self.dico['decalY'], self.dico['rayRecept'], \
                self.dico['angleRecept'], self.dico['rayReprise'], self.dico['angleReprise'], \
                self.dico['distMontee'], self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return passiveSituation(me, self.dico, *self.args_receivePass_loseMark())

## Strategie Reduire l'angle de l'attaquant adverse
class CutDownAngleStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"CutDown")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return cutDownAngle(me, 40., 20.)

## Strategie Marquer et essayer de recuperer la balle
class MarkStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Mark")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return clearSolo(me)
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
