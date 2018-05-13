# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from .tools import StateFoot
from .conditions import must_intercept, has_ball_control, is_close_goal, \
    opponent_approaches_my_goal, free_teammate, is_kick_off
from .actions import clearSolo, goToBall, goToMyGoal, cutDownAngle, pushUp, \
    passBall, goForwardsPA, goForwardsMF
from .behaviour import WithoutBallControl_GK_2v4
from .strategies import loadPath
import pickle

## Strategie Dribble + shoot
class DribbleShootStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"DribbleShoot")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if has_ball_control(me):
            return goForwardsPA(me, self.dico)
        return goToBall(me)

## Strategie Controle + dribble
class ControlDribbleStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"ControlDribble")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if has_ball_control(me):
            return goForwardsMF(me, self.dico)
        return goToBall(me)


## Strategie Revenir a la cage
class GoToMyGoalStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"GoToMyGoal")
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        return goToMyGoal(me)

## Strategie Monter
class PushUpStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"PushUp")
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        return pushUp(me)
    
## Strategie Passe
class PassStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Pass")
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        tm = free_teammate(me, 30.)
        if has_ball_control(me) and tm is not None:
            return passBall(me, tm, 4.5, 0.8)
        return goToBall(me)

## Strategie Reception d'une passe
class PassiveSituationStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"PassiveSituation")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        return WithoutBallControl_GK_2v4(me, self.dico)

## Strategie Reduire l'angle de l'attaquant adverse
class CutDownAngleStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"CutDown")
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        return cutDownAngle(me, 40., 20.)

## Strategie Marquer et essayer de recuperer la balle
class MarkStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Mark")
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if has_ball_control(me):
            return clearSolo(me)
        return goToBall(me)
