# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from .tools import StateFoot, get_random_strategy
from .conditions import must_intercept, has_ball_control, is_defensive_zone, \
    opponent_approaches_my_goal, free_teammate, is_kick_off, must_pass_ball
from .actions import beh_fonceur, shoot, shiftAside, clearSolo, goToBall, \
    goToMyGoal, tryInterception, cutDownAngle, passBall
from .behaviour import *
import pickle



def loadPath(fn):
    """
    Renvoie le chemin d'acces absolu du fichier
    passe en parametre pour la deserialisation
    d'un dictionnaire de parametres
    """
    from os.path import dirname, realpath, join
    return join(dirname(dirname(realpath(__file__))), "parameters", fn)



## Strategie aleatoire
class RandomStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self, "Random")
    def compute_strategy(self, state, id_team, id_player):
        return get_random_strategy()



"""
1v1
"""

class Fonceur1v1Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Fonceur1")
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
        # self.dico['distDefZone'] = 35.
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 1)
        if is_kick_off(me):
            return st_kickOffSolo(me, self.dico)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI']
            return WithBallControl_1v1(me, self.dico)
        return WithoutBallControl_ST_1v1(me, self.dico)



"""
2v2
"""

class Attaquant2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Attaquant2v2")
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
            # self.dico['angleInter'] = 0.81
            # self.dico['distDefZone'] = 45.
            # self.dico['distAttaque'] = 60.
            # self.dico['coeffDef'] = 2.5
        else:
            self.dico = dict()
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if is_kick_off(me):
            return st_kickOff(me, self.dico)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI']
            return WithBallControl_2v2(me, self.dico)
        return WithoutBallControl_ST_2v4(me, self.dico)



class Gardien2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Gardien2v2")
        if fn_gk is not None:
            with open(loadPath(fn_gk), "rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_st), "rb") as f:
                self.dico.update(pickle.load(f))
            # self.dico['angleInter'] = 0.81
            # self.dico['distAttaque'] = 60.
            # self.dico['distDefZone'] = 45.
            # self.dico['coeffDef'] = 2.5
        else:
            self.dico = dict()
        self.dico['n'] = -1
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if is_kick_off(me):
            return gk_kickOff(me, self.dico)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI']
            return WithBallControl_2v2(me, self.dico)
        return WithoutBallControl_GK_2v2(me, self.dico)



class CBNaif2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "CBNaif")
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
            self.dico['n'] = -1
            self.dico['tempsI'] = 4.8
            self.dico['rayDribble'] = 19.
            self.dico['rayRecept'] = 30.
            self.dico['coeffPushUp'] = 6.
            self.dico['controleAttaque'] = self.dico['controleMT']
            self.dico['distDefZone'] = 30.
        else:
            self.dico = dict()
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'], self.dico['powerPasse'], \
                self.dico['thetaPasse'], self.dico['rayPressing'], self.dico['distPasse'], \
                self.dico['angleInter'], self.dico['coeffPushUp'])
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if is_kick_off(me):
            if has_ball_control(me):
                return shoot(me, 6.)
            return goToBall(me)
        if has_ball_control(me):
            return WithBallControl_CBnaif_2v2(me, self.dico)
        return WithoutBallControl_CBnaif_2v2(me, self.dico)



"""
4v4
"""

class Attaquant4v4Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Attaquant4")
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 16.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
        self.dico['rayPressing'] = 30.
        self.dico['distDefZone'] = 75.
        self.dico['distShoot'] = 40.
        self.dico['rayPressing'] = 18.
        self.dico['angleInter'] = 0.54
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 4)
        if is_kick_off(me):
            return st_kickOffSolo(me, self.dico)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI']
            return WithBallControl_4v4(me, self.dico)
        return WithoutBallControl_ST_2v4(me, self.dico)



class Gardien4v4Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "Gardien4")
        if fn_gk is not None:
            with open(loadPath(fn_gk), "rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_st), "rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 16.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
        self.dico['distShoot'] = 40.
        self.dico['rayPressing'] = 18.
        self.dico['angleInter'] = 0.54
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 4)
        if is_kick_off(me):
            if has_ball_control(me):
                return shoot(me, 6.)
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI']
            return WithBallControl_4v4(me, self.dico)
        return WithoutBallControl_GK_4v4(me, self.dico)



class CBNaif4v4Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self, "CBNaif4")
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk), "rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 19.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
        self.dico['rayPressing'] = 18.
        self.dico['distSortie'] = 50.
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 4)
        if has_ball_control(me):
            return WithBallControl_CBnaif_4v4(me, self.dico)
        return WithoutBallControl_CBnaif_4v4(me, self.dico)



"""
Deprecated
"""

## Strategie Attaquant
"""
L'attaquant controle la balle, dribble des joueurs adverses,
fait des passes si necessaire, et frappe droit au but
lorsqu'il retrouve une belle opportunite.
Par ailleurs, il se decale vers les cotes s'il se trouve
en position de defense
"""
class AttaquantStrategy(Strategy):
    def __init__(self, fn_st=None):
        Strategy.__init__(self, "Attaquant")
        if fn_st is not None:
            with open(loadPath(fn_st), "rb") as f:
                self.dico = pickle.load(f)
        else:
            self.dico = dict()
        self.dico['distShoot'] = 36.
    def args_defense_loseMark(self):
        return (self.dico['decalX'], self.dico['decalY'])
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if has_ball_control(me):
            return WithBallControl_1v1(me, self.dico)
        if is_defensive_zone(me, self.dico['distDefZone']):
            return shiftAside(me, *self.args_defense_loseMark())
        return goToBall(me)



## Strategie Gardien
"""
Le gardien sort de sa cage lorsque la balle s'approche,
mais si elle est trop proche, le gardien essaie de l'intercepter
et fait une passe a l'un de ses coequipiers. Des que la balle a
franchi une certaine distance, le gardien monte dans le terrain
pour offrir une option de passe a ses coequipiers
"""
class GardienStrategy(Strategy):
    def __init__(self, fn_gk=None):
        Strategy.__init__(self, "Gardien")
        if fn_gk is not None:
            with open(loadPath(fn_gk), "rb") as f:
                self.dico = pickle.load(f)
        else:
            self.dico = dict()
        self.dico['tempsI'] = int(self.dico['tempsI'])
        self.dico['n'] = self.dico['tempsI']
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 2)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI']
            tm = free_teammate(me, 0.8183)
            if tm is not None and must_pass_ball(me, tm, 0.8183):
                return passBall(me, tm, 3.43, 0.0517, 12.)
            return clearSolo(me)
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, self.dico['raySortie'], self.dico['rayInter'])
        return goToMyGoal(me)



## Strategie Fonceur
"""
Le fonceur realise uniquement deux actions :
1/ il frappe la balle dès qu'il la controle
2/ il se deplace en ligne droite vers la balle
pour la recuperer
"""
class FonceurStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self, "Fonceur")
        self.alpha = 0.2
        self.beta = 0.7
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 1)
        if has_ball_control(me):
            return shoot(me, beh_fonceur(me, "normal"))
        return goToBall(me)



## Strategie FonceurChallenge1
"""
Il s'agit d'un fonceur programme specialement pour
le premier challenge, a savoir marquer le plus de
buts avec la meme configuration initial du jeu
"""
class FonceurChallenge1Strategy(Strategy):
    def __init__(self):
        Strategy.__init__(self, "FonceurChallenge1")
    def compute_strategy(self, state, id_team, id_player):
        me = StateFoot(state, id_team, id_player, 1)
        if has_ball_control(me):
            return shoot(me, beh_fonceur(me, "ch1"))
        return goToBall(me)
