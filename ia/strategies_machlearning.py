# -*- coding: utf-8 -*-
from soccersimulator import Strategy
from .tools import StateFoot
from .conditions import is_kick_off
from .strategies import loadPath
from .behaviour_machlearning import st_kick_off, gk_kick_off, attDict, defDict
import pickle

class Attaquant2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Attaquant2v2")
        self.action = None
        self.dico = dict()
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico.update(pickle.load(f))
        if fn_gk is not None:
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        self.dico['n'] = -1
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if is_kick_off(me):
            self.action = None
            return st_kick_off(me, self.dico)
        return attDict[self.action](me, self.dico)



class Defenseur2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Defenseur2v2")
        self.action = None
        self.dico = dict()
        if fn_gk is not None:
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico.update(pickle.load(f))
        self.dico['n'] = -1
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if is_kick_off(me):
            self.action = None
            return gk_kick_off(me, self.dico)
        return defDict[self.action](me, self.dico)
