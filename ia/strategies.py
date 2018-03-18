# -*- coding: utf-8 -*-
from soccersimulator import Strategy
from .tools import StateFoot, get_random_strategy, is_in_radius_action
from .conditions import must_intercept, has_ball_control, is_defensive_zone, \
        is_close_goal, is_close_ball, opponent_approaches_my_goal, must_advance
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



## Strategie aleatoire
class RandomStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Random")
    def compute_strategy(self,state,id_team,id_player):
        return get_random_strategy()



## Strategie Attaquant
"""
L'attaquant controle la balle, dribble des joueurs adverses,
fait des passes si necessaire, et frappe droit au but
lorsqu'il retrouve une belle opportunite.
Par ailleurs, il se decale vers les cotes s'il se trouve
en position de defense
"""
class AttaquantStrategy(Strategy):
    def __init__(self, alphaShoot=None, betaShoot=None, angleDribble=None, \
            powerDribble=None, distShoot=None, rayDribble=None, \
            angleGardien=None, coeffAD=None, controleMT=None, decalX=None, \
            decalY=None, distAttaque=None, controleAttaque=None, \
            distDefZone=None, fn_st=None):
        Strategy.__init__(self,"Attaquant")
        if alphaShoot is not None: # dictionnaire passe en parametre, i.e. algo genetique
            self.dico = {'alphaShoot': alphaShoot, 'betaShoot': betaShoot, \
                         'angleDribble': angleDribble, 'powerDribble': powerDribble, \
                         'distShoot': distShoot, 'rayDribble': rayDribble, \
                         'angleGardien': angleGardien, 'coeffAD': coeffAD, \
                         'controleMT': controleMT, 'decalX': decalX, 'decalY': decalY, \
                         'distAttaque': distAttaque, 'controleAttaque': controleAttaque, \
                         'distDefZone': distDefZone}
        elif fn_st is not None: # dictionnaire a charger, i.e. deserialisation
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
            self.dico['distShoot'] = 36.
        else: # dictionnaire par defaut
            self.dico = self.default_dict()
    def default_dict(self):
        alphaShoot=0.667058531634
        betaShoot=0.940268913763
        angleDribble=1.35306998836
        powerDribble=1.1365820089
        distShoot=35.8934238522
        rayDribble=14.2447275533
        angleGardien=0.841696829807
        coeffAD=0.787794696398
        controleMT=1.35035794849
        decalX=0.
        decalY=0.
        distAttaque=70.
        controleAttaque=0.98
        distDefZone=20.
        return {'alphaShoot': alphaShoot, 'betaShoot': betaShoot, 'angleDribble': angleDribble, \
                'powerDribble': powerDribble, 'distShoot': distShoot, 'rayDribble': rayDribble, \
                'angleGardien': angleGardien, 'coeffAD': coeffAD, 'controleMT': controleMT, \
                'decalX': decalX, 'decalY': decalY, 'distAttaque': distAttaque, \
                'controleAttaque': controleAttaque, 'distDefZone': distDefZone}
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
    def __init__(self, tempsI=None, rayInter=None, raySortie=None, distSortie=None, \
            distMontee=None, profDeg=None, amplDeg=None, powerDeg=None, fn_gk=None):
        Strategy.__init__(self,"Gardien")
        if tempsI is not None: # dictionnaire passe en parametre, i.e. algo genetique
            self.dico = {'tempsI': tempsI, 'rayInter': rayInter, 'raySortie': raySortie, \
                         'distSortie': distSortie, 'distMontee': distMontee, \
                         'profDeg': profDeg, 'amplDeg': amplDeg, 'powerDeg': powerDeg}
        elif fn_gk is not None: # dictionnaire a charger, i.e. deserialisation
            with open(loadPath(fn_gk),"rb") as f:
                self.dico = pickle.load(f)
            self.dico['tempsI'] = 8.
        else: # dictionnaire par defaut
            self.dico = self.default_dict()
        self.dico['tempsI'] = int(self.dico['tempsI'])
        self.dico['n'] = self.dico['tempsI']
    def default_dict(self):
        tempsI = 28.7834668136
        rayInter = 19.899498729
        raySortie = 21.4399528226
        distSortie = 66.6033785959
        distMontee = 60.
        profDeg = 0.
        amplDeg = 0.
        powerDeg = 3.
        return {'tempsI': tempsI, 'rayInter': rayInter, 'raySortie': raySortie, \
                'distSortie': distSortie, 'distMontee': distMontee, 'profDeg': profDeg, \
                'amplDeg': amplDeg, 'powerDeg': powerDeg}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            return clear(me, self.dico['profDeg'], self.dico['amplDeg'], self.dico['powerDeg'])
        '''
        if must_advance(me, self.dico['distMontee']):
            return pushUp(me)
        '''
        if must_intercept(me, self.dico['rayInter']):
            return tryInterception(me, self.dico)
        if opponent_approaches_my_goal(me, self.dico['distSortie']):
            return cutDownAngle(me, self.dico['raySortie'])
        return goToMyGoal(me)



## Strategie Dribbler
"""
C'est un joueur qui essaie toujours d'avancer balle
au pied quand il la possede, sauf s'il est dans
la surface de reparation, ou il tire la balle vers
la cage adverse
"""
class BalleAuPiedStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"BalleAuPied")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, 10.):
                return shoot(me, fonceurCh1ApprochePower)
            #return passBall(me, 10., 3., 0.8)
            return control(me, power(me))
        return receiveBall(me, 0.5)
        #return goToBall(me)



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
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return shoot(me, beh_fonceur(me, "ch1"))
        return goToBall(me)



## Strategie Attaquant (precedent)
"""
C'est un attaquant sans dribble
NB: non fonctionnel car les methodes furent modifiees
"""
class AttaquantPrecStrategy(Strategy):
    def __init__(self, alpha=0.2, beta=0.7, angleDribble=0., powerDribble=6., distShoot=27., \
            rayDribble=10., angleGardien=0.):
        Strategy.__init__(self,"Attaquant")
        self.dico = {'alpha': alpha, 'beta': beta, 'angleDribble': angleDribble, \
                     'powerDribble': powerDribble, 'distShoot': distShoot, \
                     'rayDribble': rayDribble, 'angleGardien': angleGardien}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, self.dico['distShoot']):
                shoot(me, power(self.dico['alpha'], self.dico['beta']))
            return control(me, power(me))
        if is_defensive_zone(me):
            return shiftAside(me)
        return goToBall(me)



## Strategie Gardien (precedent)
"""
C'est un gardien sans la premiere defense de la cage
ni la montee dans le terrain
NB: non fonctionnel car les methodes furent modifiees
"""
class GardienPrecStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Gardien")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            #return clearSolo(me)
            return clear(me)
        if must_intercept(me):
            return interceptBall(me,10.)
        return goToMyGoal(me)



## Strategie GardienBase
"""
 C'est un gardien qui reste toujours dans sa cage,
sauf si la balle est a une distance raisonnable,
et dans ce cas-la il fonce vers la balle pour la
degager
"""
class GardienBaseStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"GardienBase")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return clearSolo(me)
        if is_in_radius_action(me, me.my_pos, 35.):
            return goToBall(me)
        return goToMyGoal(me)
