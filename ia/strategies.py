# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from .tools import StateFoot, get_random_strategy
from .conditions import must_intercept, has_ball_control, is_defensive_zone, \
    is_close_goal, is_close_ball, opponent_approaches_my_goal, must_advance, \
    free_teammate, had_ball_control, is_kick_off, must_pass_ball, distance_horizontale, \
    both_must_kick, free_opponent
from .behaviour import beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, \
    shoot, shiftAside, clear, clearSolo, goToBall, goToMyGoal, \
    tryInterception, interceptBall, goForwardsPA, goForwardsMF, \
    cutDownAngle, pushUp, passBall, goForwardsPA_mod, goForwardsMF_mod, \
    passiveSituation, kickAt, cutDownAngle_gk, dribble, clear_gk, passiveSituationSolo, \
    mark, goForwardsDef_mod, cutDownAngle_def, loseMark
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



"""
1v1
"""

class Fonceur1v1Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Fonceur1")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'])
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'])
    def args_receivePass_loseMark(self):
        return (self.dico['decalX'], self.dico['decalY'], self.dico['rayReprise'], \
                self.dico['angleReprise'], self.dico['distMontee'], self.dico['distDefZone'], \
                self.dico['distAttaque'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player,1)
        if is_kick_off(me):
            if has_ball_control(me):
                if me.distance_ball(me.opponent_1v1().position) > 15.:
                    return goForwardsMF(me, *self.args_control_dribble_pass())
                return shoot(me, 6.)
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA(self, me, *self.args_dribble_pass_shoot())
            return goForwardsMF(me, *self.args_control_dribble_pass())
        return passiveSituationSolo(me, self.dico, *self.args_receivePass_loseMark())



"""
2v2
"""

class Attaquant2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Attaquant2v2")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
            self.dico['angleInter'] = 0.81
            self.dico['distDefZone'] = 30.
            self.dico['distAttaque'] = 60.
            self.dico['coeffDef'] = 2.5
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.kickoff = 0
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'], \
                self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['rayPressing'], \
                self.dico['distPasse'], self.dico['angleInter'], self.dico['coeffPushUp'])
    def args_receivePass_loseMark(self):
        return (self.dico['decalX'], self.dico['decalY'], self.dico['rayRecept'], \
                self.dico['angleRecept'], self.dico['rayReprise'], self.dico['angleReprise'], \
                self.dico['distMontee'], self.dico['coeffPushUp'], self.dico['distDefZone'], \
                self.dico['rayPressing'], self.dico['distAttaque'])
    def args_control_dribble_pass(self, coeffDef):
        return (self.dico['angleDribble'], coeffDef*self.dico['powerDribble'], \
                self.dico['rayDribble'], self.dico['coeffAD'], self.dico['controleMT'], \
                coeffDef*self.dico['powerPasse'], self.dico['thetaPasse'], \
                self.dico['rayPressing'], self.dico['distPasse'], self.dico['angleInter'], \
                self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player, 2)
        self.kickoff += 1
        if is_kick_off(self, me):
            if has_ball_control(me):
                count = both_must_kick(me)
                if count == 2:
                    return shoot(me,6.)
                if count == 1:
                    return kickAt(me, Vector2D(me.opp_goal.x, 100.),6.)
                return goForwardsMF_mod(me, *self.args_control_dribble_pass(1.))
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_defensive_zone(me, self.dico['distDefZone']):
                return goForwardsDef_mod(me, *self.args_control_dribble_pass(self.dico['coeffDef']))
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, *self.args_control_dribble_pass(1.))
        return passiveSituation(me, self.dico, *self.args_receivePass_loseMark())



class Gardien2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Gardien2v2")
        if fn_gk is not None:
            with open(loadPath(fn_gk),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_st),"rb") as f:
                self.dico.update(pickle.load(f))
            self.dico['angleInter'] = 0.81
            self.dico['distAttaque'] = 60.
            self.dico['distDefZone'] = 30.
            self.dico['coeffDef'] = 2.5
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.kickoff = 0
    def args_dribble_pass_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'], \
                self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['rayPressing'], \
                self.dico['distPasse'], self.dico['angleInter'], self.dico['coeffPushUp'])
    def args_control_dribble_pass(self, coeffDef):
        return (self.dico['angleDribble'], coeffDef*self.dico['powerDribble'], \
                self.dico['rayDribble'], self.dico['coeffAD'], self.dico['controleMT'], \
                coeffDef*self.dico['powerPasse'], self.dico['thetaPasse'], \
                self.dico['rayPressing'], self.dico['distPasse'], self.dico['angleInter'], \
                self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player, 2)
        self.kickoff += 1
        if is_kick_off(self, me):
            if me.distance(me.ball_pos) < 30. and me.distance_ball(me.nearest_opp.position) > 35.:
                return cutDownAngle_gk(me, self.dico['distMontee'])
            if has_ball_control(me):
                count = both_must_kick(me)
                if count >= 1:
                    return shoot(me,6.)
                return cutDownAngle_gk(me, self.dico['distMontee'])
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_defensive_zone(me, self.dico['distDefZone']):
                return goForwardsDef_mod(me, *self.args_control_dribble_pass(self.dico['coeffDef']))
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, *self.args_control_dribble_pass(1.))
        if me.is_nearest_ball() or had_ball_control(me, self.dico['rayReprise'], self.dico['angleReprise']):
            return tryInterception(me, self.dico)
        if distance_horizontale(me.ball_pos, me.opp_goal) < self.dico['distAttaque']  and \
           me.ball_speed.dot(me.attacking_vector) >= 0. and me.is_nearest_ball_my_team():
            return tryInterception(me, self.dico)
        if is_defensive_zone(me, self.dico['distDefZone']+30.) and me.team_controls_ball():
            return loseMark(me, 25., 45.)
        if must_advance(me, self.dico['distMontee']):
            return pushUp(me, self.dico['coeffPushUp'])
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        if me.distance_ball(me.my_goal) < 30.:
            return goToBall(me)
        if me.distance_ball(me.my_pos) < 40. and me.is_nearest_ball_my_team():
            return tryInterception(me, self.dico)
        # if opponent_approaches_my_goal(me, self.dico['distSortie']):
        #     return goToMyGoal(me)
        # opp = free_opponent(me, self.dico['distAttaque'], self.dico['rayPressing'])
        opp = free_opponent(me, 60., self.dico['rayPressing'])
        if opp is not None:
            return mark(me, opp, 20.)
        return cutDownAngle_def(me, self.dico['distMontee']+10., self.dico['rayInter'])



class CBNaif2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"CBNaif")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
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
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player,2)
        if is_kick_off(me):
            if has_ball_control(me):
                return shoot(me,6.)
            return goToBall(me)
        if has_ball_control(me):
            tm = free_teammate(me, self.dico['angleInter'])
            if tm is not None and must_pass_ball(me, tm, self.dico['distPasse'], self.dico['angleInter']):
                return passBall(me, tm, 2.*self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['coeffPushUp'])
            return clear_gk(me)# + goToMyGoal(me)
        if me.is_nearest_ball():
            return tryInterception(me, self.dico)
        if must_intercept(me, self.dico['rayInter']) and me.distance_ball(me.my_goal) < self.dico['distMontee']-20:
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, 20., 10.)
        return cutDownAngle_gk(me, self.dico['distMontee']-20.)



"""
4v4
"""

class Attaquant4v4Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Attaquant4")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
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
        self.precedent = None
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
                self.dico['distMontee'], self.dico['coeffPushUp'], self.dico['distDefZone'], \
                self.dico['rayPressing'], self.dico['distAttaque'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player, 4)
        if is_kick_off(me):
            if has_ball_control(me):
                count = both_must_kick(me)
                if count >= 2:
                    return shoot(me,6.)
                if count == 1:
                    return kickAt(me, Vector2D(me.opp_goal.x, 100.),6.)
                return goForwardsMF_mod(me, self, *self.args_control_dribble_pass())
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, self, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, self, *self.args_control_dribble_pass())
        return passiveSituation(me, self.dico, *self.args_receivePass_loseMark())



class Gardien4v4Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"Gardien4")
        if fn_gk is not None:
            with open(loadPath(fn_gk),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_st),"rb") as f:
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
        self.precedent = None
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
        me = StateFoot(state,id_team,id_player, 4)
        if is_kick_off(me):
            if has_ball_control(me):
                return shoot(me,6.)
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, self, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, self, *self.args_control_dribble_pass())
        if me.is_nearest_ball() or had_ball_control(me, self.dico['rayReprise'], self.dico['angleReprise']):
            return tryInterception(me, self.dico)
        if distance_horizontale(me.ball_pos, me.opp_goal) < self.dico['distAttaque']  and \
           me.ball_speed.dot(me.attacking_vector) >= 0. and me.is_nearest_ball_my_team():
            return tryInterception(me, self.dico)
        if must_advance(me, self.dico['distMontee']):
            return pushUp(me, self.dico['coeffPushUp'])
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        if me.distance_ball(me.my_goal) < 30.:
            return goToBall(me)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return goToMyGoal(me)
        return cutDownAngle_gk(me, self.dico['distMontee'])



class CBNaif4v4Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"CBNaif4")
        if fn_st is not None:
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            with open(loadPath(fn_gk),"rb") as f:
                self.dico.update(pickle.load(f))
        else:
            self.dico = dict()
        self.dico['n'] = -1
        self.dico['tempsI'] = 4.8
        self.dico['rayDribble'] = 19.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
    def args_control_dribble_pass(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'], self.dico['powerPasse'], \
                self.dico['thetaPasse'], self.dico['rayPressing'], self.dico['distPasse'], \
                self.dico['angleInter'], self.dico['coeffPushUp'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player,4)
        if has_ball_control(me):
            tm = free_teammate(me, self.dico['angleInter'])
            if tm is not None and must_pass_ball(me, tm, self.dico['distPasse'], self.dico['angleInter']):
                return passBall(me, tm, 2.*self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['coeffPushUp']) + goToMyGoal(me)
            return clear_gk(me) + goToMyGoal(me)
        if me.is_nearest_ball():
            return tryInterception(me, self.dico)
        if must_intercept(me, self.dico['rayInter']) and me.distance_ball(me.my_goal) < self.dico['distMontee']-20:
            return goToBall(me)
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, 20., 10.)
        return cutDownAngle_gk(me, self.dico['distMontee']-25.)



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
        me = StateFoot(state,id_team,id_player, 2)
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
        me = StateFoot(state,id_team,id_player,2)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            tm = free_teammate(me, 0.8183)
            if tm is not None and must_pass_ball(me, tm, 50., 0.8183):
                return passBall(me, tm, 3.43, 0.0517, 12.)
            return clearSolo(me)
        '''
        if must_advance(me, self.dico['distMontee']):
            return pushUp(me, self.dico['coeffPushUp'])
        '''
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
        Strategy.__init__(self,"Fonceur")
        self.alpha = 0.2
        self.beta = 0.7
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player,1)
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
        Strategy.__init__(self,"FonceurChallenge1")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player,1)
        if has_ball_control(me):
            return shoot(me, beh_fonceur(me, "ch1"))
        return goToBall(me)
