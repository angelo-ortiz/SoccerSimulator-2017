# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from .tools import StateFoot, get_random_strategy, is_in_radius_action, nearest_defender
from .conditions import must_intercept, has_ball_control, is_defensive_zone, \
        is_close_goal, is_close_ball, opponent_approaches_my_goal, must_advance, \
        free_teammate, had_ball_control, is_kick_off, must_pass_ball, distance_horizontale
from .behaviour import beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, \
    shoot, shiftAside, clear, clearSolo, goToBall, goToMyGoal, \
    tryInterception, interceptBall, fonceurCh1ApprochePower, shootPower, \
    power, goForwardsPA, goForwardsMF, cutDownAngle, pushUp, passBall, \
    goForwardsPA_mod, goForwardsMF_mod, passiveSituation, kickAt, \
    cutDownAngle_gk, dribble, clear_gk, passiveSituationSolo
import pickle

#TODO si la balle arrive vers le joueur (vecteurs "opposes"), il faut
# prendre en compte sa vitesse d'arrivee, notamment en ajoutant
# ce vecteur au control prealable

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
        self.dico['rayDribble'] = 16.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
        self.dico['rayPressing'] = 30.
        self.dico['distDefZone'] = 75.
        self.dico['distShoot'] = 40.
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
                return kickAt(me, Vector2D(me.opp_goal.x, 100.),6.)
            return goToBall(me)
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
        self.dico['rayDribble'] = 16.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
        self.dico['distShoot'] = 40.
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
                return goForwardsPA_mod(me, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, *self.args_control_dribble_pass())
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



class GardienModif2v2Strategy(Strategy):
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
        self.dico['rayDribble'] = 19.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
        self.dico['distShoot'] = 40.
        self.dico['distDefZone'] = 40.
        self.dico['powerDribble'] = 3.2
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
        me = StateFoot(state,id_team,id_player, 2)
        if is_kick_off(me):
            if me.distance(me.ball_pos) < 30. and me.distance_ball(me.nearest_opp.position) > 35.:
                return cutDownAngle_gk(me, self.dico['distMontee'])#goForwardsMF(me, *self.args_control_dribble_pass())
            if has_ball_control(me):
                return shoot(me,6.)
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            tm = free_teammate(me, self.dico['angleInter'])
            if is_defensive_zone(me, self.dico['distDefZone']):
                if tm is not None and must_pass_ball(me, tm, self.dico['distPasse'], self.dico['angleInter']):
                    return passBall(me, tm, 2.*self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['coeffPushUp'])# + goToMyGoal(me)
                return clear_gk(me, angleClear=1.2)# + goToMyGoal(me)
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, *self.args_control_dribble_pass())
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
        return cutDownAngle_gk(me, self.dico['distMontee']+20.)



class AttaquantModif2v2Strategy(Strategy):
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
        self.dico['rayDribble'] = 19.
        self.dico['rayRecept'] = 30.
        self.dico['coeffPushUp'] = 6.
        self.dico['controleAttaque'] = self.dico['controleMT']
        self.dico['rayPressing'] = 30.
        self.dico['distDefZone'] = 40.
        self.dico['distShoot'] = 40.
        self.dico['powerDribble'] = 3.2
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
        me = StateFoot(state,id_team,id_player, 2)
        if is_kick_off(me):
            if has_ball_control(me):
                if me.distance_ball(me.nearest_opp.position) > 15.:
                    return goForwardsMF_mod(me, *self.args_control_dribble_pass())
                return kickAt(me, Vector2D(me.opp_goal.x, 100.),6.)
            return goToBall(me)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            tm = free_teammate(me, self.dico['angleInter'])
            if is_defensive_zone(me, self.dico['distDefZone']):
                if tm is not None and must_pass_ball(me, tm, self.dico['distPasse'], self.dico['angleInter']):
                    return passBall(me, tm, 2.*self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['coeffPushUp'])# + goToMyGoal(me)
                return clear_gk(me, angleClear=1.2)# + goToMyGoal(me)
            if is_close_goal(me, self.dico['distAttaque']):
                return goForwardsPA_mod(me, *self.args_dribble_pass_shoot())
            return goForwardsMF_mod(me, *self.args_control_dribble_pass())
        return passiveSituation(me, self.dico, *self.args_receivePass_loseMark())



class CBNaif2v2Strategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"CBNaif")
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
        self.dico['distDefZone'] = 30.
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
                return passBall(me, tm, 2.*self.dico['powerPasse'], self.dico['thetaPasse'], self.dico['coeffPushUp'])# + goToMyGoal(me)
            return clear_gk(me)# + goToMyGoal(me)
        if me.is_nearest_ball():
            return tryInterception(me, self.dico)
        if must_intercept(me, self.dico['rayInter']) and me.distance_ball(me.my_goal) < self.dico['distMontee']-20:
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, 20., 10.)
        return cutDownAngle_gk(me, self.dico['distMontee']-20.)



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
            return pushUp(me)#, self.dico['coeffPushUp']
        '''
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, self.dico['raySortie'], self.dico['rayInter'])
        return goToMyGoal(me)



class CBNaifStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"CBNaif")
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
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, 20., 10.)
        return cutDownAngle_gk(me, self.dico['distMontee']-20.)



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
            #return shoot(me, shootPower(me, self.alpha, self.beta))
        return goToBall(me)

class FonceurModifStrategy(Strategy):
    def __init__(self, fn_gk=None, fn_st=None):
        Strategy.__init__(self,"FonceurModif")
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




