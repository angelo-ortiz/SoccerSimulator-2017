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
    goForwardsPA_mod, goForwardsMF_mod, passiveSituation, kickAt, \
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



## Strategie aleatoire
class RandomStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Random")
    def compute_strategy(self,state,id_team,id_player):
        return get_random_strategy()



class AttaquantModifStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"AttaquantModif")
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
        """
        if me.distance_ball(me.my_goal) < self.dico['rayInter']:
            if has_ball_control(me):
                oppDef = nearest_defender(me, me.opponents, self.dico['rayDribble'])
                if oppDef is not None:
                    return dribble(me,oppDef, self.dico['angleDribble'], 6., self.dico['coeffAD'])
                return clearSolo(me)
            return tryInterception(me, self.dico)
            #return goToBall(me)
        """
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, *self.args_control_dribble_pass())
        return passiveSituation(me, self.dico, *self.args_receivePass_loseMark())



class GardienModifStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"GardienModif")
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
        """
        if me.distance_ball(me.my_goal) < self.dico['rayInter']:
            if has_ball_control(me):
                oppDef = nearest_defender(me, me.opponents, self.dico['rayDribble'])
                if oppDef is not None:
                    return dribble(me,oppDef, self.dico['angleDribble'], 6., self.dico['coeffAD'])
                return clearSolo(me)
            return tryInterception(me, self.dico)
            #return goToBall(me)
        """
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, *self.args_control_dribble_pass())
        if had_ball_control(me, self.dico['rayReprise'], self.dico['angleReprise']):
            #return goToBall(me)
            return tryInterception(me, self.dico)
        if me.is_nearest_ball():
            return tryInterception(me, self.dico)
            #return goToBall(me)
        if must_advance(me, self.dico['distMontee']):
            return pushUp(me, self.dico['coeffPushUp'])
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return goToMyGoal(me)
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        return cutDownAngle_gk(me, self.dico['distMontee'])



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
        Strategy.__init__(self,"Attaquant")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
        else:
            self.dico = dict()
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
        Strategy.__init__(self,"Gardien")
        if fn_gk is not None:
            with open(loadPath(fn_gk),"rb") as f:
                self.dico = pickle.load(f)
        else:
            self.dico = dict()
        self.dico['tempsI'] = int(self.dico['tempsI'])
        self.dico['n'] = self.dico['tempsI']
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            return clear(me, self.dico['profDeg'], self.dico['amplDeg'], self.dico['powerDeg'])
        '''
        if must_advance(me, self.dico['distMontee']):
            return pushUp(me)#, self.dico['coeffPushUp']
        '''
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, self.dico['raySortie'], self.dico['rayInter'])
        return goToMyGoal(me)



class CBNaifStrategy(Strategy):
    def __init__(self, fn_gk=None):
        Strategy.__init__(self,"CBNaif")
        if fn_gk is not None:
            with open(loadPath(fn_gk),"rb") as f:
                self.dico = pickle.load(f)
        else:
            self.dico = dict()
        self.dico['tempsI'] = int(self.dico['tempsI'])
        self.dico['n'] = self.dico['tempsI']
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return clearSolo(me)
        if me.distance(me.my_goal) > 25.:
            return goToMyGoal(me)
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, 20., 10.)
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
        Strategy.__init__(self,"Fonceur")
        self.alpha = 0.2
        self.beta = 0.7
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return shoot(me, beh_fonceur(me, "normal"))
            #return shoot(me, shootPower(me, self.alpha, self.beta))
        return goToBall(me)
