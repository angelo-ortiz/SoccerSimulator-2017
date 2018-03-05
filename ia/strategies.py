from soccersimulator import Strategy
from .tools import StateFoot, get_random_strategy, get_empty_strategy, is_in_radius_action
from .conditions import must_intercept_gk, has_ball_control, temps_interception, is_in_box, is_defense_zone, \
        is_close_goal, is_close_ball, must_defend_goal, must_advance
from .behaviour import shoot, beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, controler, decaler,\
        foncer, degager, degager_solo, aller_vers_balle, aller_vers_cage, intercepter_balle, \
        fonceurCh1ApprochePower, forceShoot, power, essayerBut, avancerBalle, defendre_SR, monterTerrain

## Strategie aleatoire
class RandomStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Random")
    def compute_strategy(self,state,id_team,id_player):
        return get_random_strategy()

## Strategie Fonceur
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
class FonceurChallenge1Strategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"FonceurChallenge1")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return foncer(me, beh_fonceur(me, "ch1"))
        return aller_vers_balle(me)

#tempsI : 28.7834668136
#rayInter : 19.899498729
#distSortie : 66.6033785959
#raySortie : 21.4399528226
#alphaShoot : 0.667058531634
#betaShoot : 0.940268913763
#angleDribble : 1.35306998836
#powerDribble : 1.1365820089
#distShoot : 35.8934238522
#distDribble : 14.2447275533
#angleGardien : 0.841696829807
#coeffAD : 0.787794696398
#powerControl : 1.35035794849

## Strategie Attaquant
class AttaquantStrategy(Strategy):
    def __init__(self, alphaShoot=0.667058531634, betaShoot=0.940268913763, angleDribble=1.35306998836, powerDribble=1.1365820089, distShoot=35.8934238522, rayDribble=14.2447275533, angleGardien=0.841696829807, coeffAD=0.787794696398, powerControl=1.35035794849):
        Strategy.__init__(self,"Attaquant")
        self.dictST = {'alphaShoot': alphaShoot, 'betaShoot': betaShoot, 'angleDribble': angleDribble, 'powerDribble': powerDribble, 'distShoot': distShoot, 'rayDribble': rayDribble, 'angleGardien': angleGardien, 'coeffAD': coeffAD, 'powerControl': powerControl}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, self.dictST['distShoot']):
                return essayerBut(self, me, self.dictST['alphaShoot'], self.dictST['betaShoot'], self.dictST['angleDribble'], self.dictST['powerDribble'], self.dictST['rayDribble'], self.dictST['angleGardien'], self.dictST['coeffAD'], self.dictST['powerControl'])
            return avancerBalle(me, self.dictST['angleDribble'], self.dictST['powerDribble'], self.dictST['rayDribble'], self.dictST['coeffAD'], self.dictST['powerControl'])
        if is_defense_zone(me):
            return decaler(me)
        return aller_vers_balle(me)

## Strategie Attaquant
class AttaquantPrecStrategy(Strategy):
    def __init__(self, alpha=0.2, beta=0.7, angleDribble=0., powerDribble=6., distShoot=27., rayDribble=10., angleGardien=0.):
        Strategy.__init__(self,"Attaquant")
        self.dictST = {'alpha': alpha, 'beta': beta, 'angleDribble': angleDribble, 'powerDribble': powerDribble, 'distShoot': distShoot, 'rayDribble': rayDribble, 'angleGardien': angleGardien}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, self.dictST['distShoot']):
                foncer(me, power(self.dictST['alpha'], self.dictST['beta']))
            return controler(me, power(me))
        if is_defense_zone(me):
            return decaler(me)
        return aller_vers_balle(me)

## Strategie Dribbler
class BalleAuPiedStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"BalleAuPied")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_in_box(me):
                return foncer(me, fonceurCh1ApprochePower)
            return controler(me, power(me))
        return aller_vers_balle(me)

## Strategie Gardien
class GardienStrategy(Strategy):
    #def __init__(self, tempsI=6, n=6, rayInter=15.):
    def __init__(self, tempsI=28.7834668136, n=0, rayInter=19.899498729, raySortie=21.4399528226, distSortie=66.6033785959, distMontee=60.):
    #def __init__(self, tempsI=15.189582048077039, n=0, rayInter=27.308626539829262):
        Strategy.__init__(self,"Gardien")
        n = tempsI #TODO ajout ???
        self.dictGK = {'tempsI': tempsI, 'n': n, 'rayInter': rayInter, 'raySortie': raySortie, 'distSortie': distSortie, 'distMontee': distMontee}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            self.dictGK['n'] = self.dictGK['tempsI'] - 1
            return degager(me)
        """if must_advance(me, self.dictGK['distMontee']):
            return monterTerrain(me) 
        """
        if must_intercept_gk(me, self.dictGK['rayInter']):
            self.dictGK['n'] -= 1
            if self.dictGK['n'] <= 0 :
                self.dictGK['n'] = self.dictGK['tempsI'] - 1
                return get_empty_strategy()
            return intercepter_balle(self, me,self.dictGK['n'])
        if must_defend_goal(me, self.dictGK['distSortie']):
            return defendre_SR(me, self.dictGK['raySortie'])
        return aller_vers_cage(me)

## Strategie Gardien
class GardienPrecStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Gardien")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            #return degager_solo(me)
            return degager(me)
        if must_intercept_gk(me):
            return intercepter_balle(me,10.)
        return aller_vers_cage(me)

## Strategie GardienBase
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
