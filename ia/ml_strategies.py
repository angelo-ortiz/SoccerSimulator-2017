# -*- coding: utf-8 -*-
from soccersimulator import Strategy
from .tools import StateFoot
from .conditions import is_kick_off
from .strategies import loadPath
from .ml_behaviour import st_kick_off_solo, st_kick_off, gk_kick_off, \
    fonDict, attDict, defDict
import numpy as np
import random
import pickle

class Fonceur1v1Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Fonceur1v1")
        self.action = None
        self.dico = dict()
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico.update(pickle.load(f))
        if fn_gk is not None:
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 1)
        if is_kick_off(me):
            self.action = None
            return st_kick_off_solo(me, self.dico)
        return fonDict[self.action](me, self.dico)



class Fonceur1v1MLStrategy(Strategy):
    def __init__(self, fn_fon, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Fonceur1v1ML")
        self.action = None
        self.dico = dict()
        if fn_fon is not None:
            with open(loadPath(fn_fon), "rb") as f:
                self.playerQTable = pickle.load(f)
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico.update(pickle.load(f))
        if fn_gk is not None:
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
        self.dico['n'] = -1
    def q(self, state, action=None):
        if state not in self.playerQTable:
            self.playerQTable[state] = np.zeros(len(fonDict))
        if action is None:
            return self.playerQTable[state]
        return self.playerQTable[state][action]
    def chooseAction(self, state):
        qT = self.q(state)
        indices = np.argwhere(qT == np.amax(qT)).flatten().tolist()
        self.action = random.choice(indices)
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 1)
        self.chooseAction(me)
        if is_kick_off(me):
            self.action = None
            return st_kick_off_solo(me, self.dico)
        return fonDict[self.action](me, self.dico)



class Attaquant2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Attaquant2v2")
        self.action = None
        self.dico = dict()
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico.update(pickle.load(f))
        if fn_gk is not None:
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if is_kick_off(me):
            self.action = None
            return st_kick_off(me, self.dico)
        return attDict[self.action](me, self.dico)



class Defenseur2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Defenseur2v2")
        self.action = None
        self.dico = dict()
        if fn_gk is not None:
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico.update(pickle.load(f))
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if is_kick_off(me):
            self.action = None
            return gk_kick_off(me, self.dico)
        return defDict[self.action](me, self.dico)
