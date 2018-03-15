# -*- coding: utf-8 -*-
from soccersimulator import Strategy
from .tools import StateFoot, get_random_strategy, get_empty_strategy, is_in_radius_action
from .conditions import must_intercept, has_ball_control, temps_interception, is_defense_zone, \
        is_close_goal, is_close_ball, must_defend_goal, must_advance
from .behaviour import shoot, beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, controler, decaler,\
        foncer, degager, degager_solo, aller_vers_balle, aller_vers_cage, intercepter_balle, \
        fonceurCh1ApprochePower, forceShoot, power, essayerBut, avancerBalle, defendre_SR, monterTerrain
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
            return foncer(me, beh_fonceur(me, "normal"))
            #return foncer(me, forceShoot(me, self.alpha, self.beta))
        return aller_vers_balle(me)



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
            return foncer(me, beh_fonceur(me, "ch1"))
        return aller_vers_balle(me)

## Strategie Attaquant
"""
L'attaquant controle la balle, dribble des joueurs adverses,
fait des passes si necessaire, et frappe droit au but
lorsqu'il retrouve une belle opportunite.
Par ailleurs, il se decale vers les cotes s'il se trouve
en position de defense
"""
class AttaquantStrategy(Strategy):
    def __init__(self, alphaShoot=None, betaShoot=None, angleDribble=None, powerDribble=None, \
            distShoot=None, rayDribble=None, angleGardien=None, coeffAD=None, controleMT=None, \
            decalX=None, decalY=None, distAttaque=None, controleAttaque=None, distDefZone=None, fn_st=None):
        Strategy.__init__(self,"Attaquant")
        if alphaShoot is not None: # dictionnaire passe en parametre, i.e. algo genetique
            self.dico = {'alphaShoot': alphaShoot, 'betaShoot': betaShoot, 'angleDribble': angleDribble, \
                         'powerDribble': powerDribble, 'distShoot': distShoot, 'rayDribble': rayDribble, \
                         'angleGardien': angleGardien, 'coeffAD': coeffAD, 'controleMT': controleMT, \
                         'decalX': decalX, 'decalY': decalY, 'distAttaque': distAttaque, \
                         'controleAttaque': controleAttaque, 'distDefZone': distDefZone}
        elif fn_st is not None: # dictionnaire a charger, i.e. deserialisation
            with open(loadPath(fn_st),"rb") as f:
                self.dico = pickle.load(f)
        else: # dictionnaire par defaut
            self.dico = self.default_dict()
    def default_dict(self):
        alphaShoot=0.667058531634
        betaShoot=0.940268913763
        angleDribble=1.35306998836
        powerDribble=1.1365820089
        distShoot=35.8934238522
        rayDribble=14.2447275533#20.
        angleGardien=0.841696829807
        coeffAD=0.787794696398
        controleMT=1.35035794849#1.1
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
    def args_dribble_passe_shoot(self):
        return (self.dico['alphaShoot'], self.dico['betaShoot'], self.dico['angleDribble'], \
                self.dico['powerDribble'], self.dico['rayDribble'], self.dico['angleGardien'], \
                self.dico['coeffAD'], self.dico['controleAttaque'], self.dico['distShoot'])
    def args_controle_dribble_passe(self):
        return (self.dico['angleDribble'], self.dico['powerDribble'], self.dico['rayDribble'], \
                self.dico['coeffAD'], self.dico['controleMT'])
    def args_defense_demarquage(self):
        return (self.dico['decalX'], self.dico['decalY'])
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, self.dico['distAttaque']):
                return essayerBut(self, me, *self.args_dribble_passe_shoot())
            return avancerBalle(me, *self.args_controle_dribble_passe())
        if is_defense_zone(me, self.dico['distDefZone']):
            return decaler(me, *self.args_defense_demarquage())
        return aller_vers_balle(me)

## Strategie Attaquant
"""
C'est un attaquant sans dribble
NB: non fonctionnel car les methodes furent modifiees
"""
class AttaquantPrecStrategy(Strategy):
    def __init__(self, alpha=0.2, beta=0.7, angleDribble=0., powerDribble=6., distShoot=27., \
            rayDribble=10., angleGardien=0.):
        Strategy.__init__(self,"Attaquant")
        self.dico = {'alpha': alpha, 'beta': beta, 'angleDribble': angleDribble, 'powerDribble': powerDribble, \
                     'distShoot': distShoot, 'rayDribble': rayDribble, 'angleGardien': angleGardien}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, self.dico['distShoot']):
                foncer(me, power(self.dico['alpha'], self.dico['beta']))
            return controler(me, power(me))
        if is_defense_zone(me):
            return decaler(me)
        return aller_vers_balle(me)

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
                return foncer(me, fonceurCh1ApprochePower)
            return controler(me, power(me))
        return aller_vers_balle(me)

## Strategie Gardien
"""
Le gardien sort de sa cage lorsque la balle s'approche,
mais si elle est trop proche, le gardien essaie de l'intercepter
et fait une passe a l'un de ses coequipiers. Des que la balle a
franchi une certaine distance, le gardien monte dans le terrain
pour offrir une option de passe a ses coequipiers
"""
class GardienStrategy(Strategy):
    def __init__(self, tempsI=None, n=None, rayInter=None, raySortie=None, distSortie=None, \
            distMontee=None, profDeg=None, amplDeg=None, powerDeg=None, fn_gk=None):
        Strategy.__init__(self,"Gardien")
        if tempsI is not None: # dictionnaire passe en parametre, i.e. algo genetique
            self.dico = {'tempsI': tempsI, 'rayInter': rayInter, 'raySortie': raySortie, \
                         'distSortie': distSortie, 'distMontee': distMontee, 'profDeg': profDeg, \
                         'amplDeg': amplDeg, 'powerDeg': powerDeg}
        elif fn_gk is not None: # dictionnaire a charger, i.e. deserialisation
            with open(loadPath(fn_gk),"rb") as f:
                self.dico = pickle.load(f)
            #self.dico['powerDeg'] = 3.813968360114573
            #self.dico['raySortie'] = 21.4399528226
            #self.dico['amplDeg'] = 21.4399528226
        else: # dictionnaire par defaut
            self.dico = self.default_dict()
        self.dico['n'] = self.dico['tempsI']
    def default_dict(self):
        tempsI = 28.7834668136#7
        rayInter = 19.899498729
        raySortie = 21.4399528226
        distSortie = 66.6033785959
        distMontee = 60.
        profDeg = 0.
        amplDeg = 0.
        powerDeg = 3.
        return {'tempsI': tempsI, 'rayInter': rayInter, 'raySortie': raySortie, 'distSortie': distSortie, \
                'distMontee': distMontee, 'profDeg': profDeg, 'amplDeg': amplDeg, 'powerDeg': powerDeg}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            self.dico['n'] = self.dico['tempsI'] - 1
            return degager(me, self.dico['profDeg'], self.dico['amplDeg'], self.dico['powerDeg'])
        '''
        if must_advance(me, self.dico['distMontee']):
            return monterTerrain(me)
        '''
        if must_intercept(me, self.dico['rayInter']):
            self.dico['n'] -= 1
            if self.dico['n'] <= 0 :
                self.dico['n'] = self.dico['tempsI'] - 1
                return get_empty_strategy()
            return intercepter_balle(self, me,self.dico['n'])
        if must_defend_goal(me, self.dico['distSortie']):
            return defendre_SR(me, self.dico['raySortie'])
        return aller_vers_cage(me)

## Strategie Gardien
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
            #return degager_solo(me)
            return degager(me)
        if must_intercept(me):
            return intercepter_balle(me,10.)
        return aller_vers_cage(me)

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
            return degager_solo(me)
        if is_in_radius_action(me, me.my_pos, 35.):
            return aller_vers_balle(me)
        return aller_vers_cage(me)
