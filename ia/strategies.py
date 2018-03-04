from soccersimulator import Strategy
from .tools import StateFoot, get_random_strategy, get_empty_strategy, is_in_radius_action
from .conditions import must_intercept_gk, can_shoot, temps_interception, is_in_box, is_defense_zone, is_close_goal, is_close_ball
from .behaviour import shoot, beh_fonceurNormal, beh_fonceurChallenge1, beh_fonceur, controler, decaler,\
        foncer, degager, degager_solo, aller_vers_balle, aller_vers_cage, intercepter_balle, \
        fonceurCh1ApprochePower, forceShoot, power, essayerBut, avancerBalle

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
        if can_shoot(me):
            return foncer(me, beh_fonceur(me, "normal"))
            #return foncer(me, forceShoot(me, self.alpha, self.beta))
        return aller_vers_balle(me)

## Strategie FonceurChallenge1
class FonceurChallenge1Strategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"FonceurChallenge1")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return foncer(me, beh_fonceur(me, "ch1"))
        return aller_vers_balle(me)

## Strategie Attaquant
class AttaquantStrategy(Strategy):
    #def __init__(self, alpha=0.2, beta=0.7, angleDribble=0., powerDribble=6., distShoot=27., distDribble=10., angleGardien=0.):
    #def __init__(self, alpha=0.5700617892748253, beta=0.9687075326265157, angleDribble=-0.05111838400840796, powerDribble=1.1307188761187168, distShoot=44.05783413958745, distDribble=15.204489315456959, angleGardien=0.20031270839106471):
    #def __init__(self, alpha=0.34872582965235477, beta=0.5938091014432113, angleDribble=-1.3571175260326729, powerDribble=5.492782232619749, distShoot=56.168043983702184, distDribble=26.165301649104013, angleGardien=0.14071454319593008):
    #def __init__(self, alpha=0.029328380536960852, beta=0.8102839933444099, angleDribble=0.2383687440209621, powerDribble=5.408480987627415, distShoot=39.31577385201216, distDribble=22.964594297665375, angleGardien=0.22071454319593008):
    def __init__(self, alpha=0.2, beta=0.7, angleDribble=1.4359552093859227, powerDribble=5.836715877613142, distShoot=40.35131904440021, distDribble=21.019052895101332, angleGardien=0.22071454319593008, coeffAD=1.2968508106333991):
    #def __init__(self, alpha=0.713577041027907, beta=0.9539444724213427, angleDribble=1.4359552093859227, powerDribble=5.836715877613142, distShoot=40.35131904440021, distDribble=21.019052895101332, angleGardien=0.22071454319593008, coeffAD=1.2968508106333991):
    #def __init__(self, alpha=0.3540815114563497, beta=0.43085151335168564, angleDribble=1.4359552093859227, powerDribble=5.836715877613142, distShoot=60.35131904440021, distDribble=21.019052895101332, angleGardien=0.22071454319593008, coeffAD=1.2968508106333991):
    #def __init__(self, alpha=0.3540815114563497, beta=0.43085151335168564, angleDribble=1.4359552093859227, powerDribble=5.836715877613142, distShoot=60.35131904440021, distDribble=21.019052895101332, angleGardien=0.22071454319593008, coeffAD=0.7930914652976095):
        Strategy.__init__(self,"Attaquant")
        self.dictST = {'alpha': alpha, 'beta': beta, 'angleDribble': angleDribble, 'powerDribble': powerDribble, 'distShoot': distShoot, 'distDribble': distDribble, 'angleGardien': angleGardien, 'coeffAD': coeffAD}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            if is_close_goal(me, self.dictST['distShoot']):
                return essayerBut(me, self.dictST['alpha'], self.dictST['beta'], self.dictST['angleDribble'], self.dictST['powerDribble'], self.dictST['distDribble'], self.dictST['angleGardien'], self.dictST['coeffAD'])
            return avancerBalle(me, self.dictST['angleDribble'], self.dictST['powerDribble'], self.dictST['distDribble'], self.dictST['coeffAD'])
        if is_defense_zone(me):
            return decaler(me)
        return aller_vers_balle(me)

## Strategie Attaquant
class AttaquantPrecStrategy(Strategy):
    def __init__(self, alpha=0.2, beta=0.7, angleDribble=0., powerDribble=6., distShoot=27., distDribble=10., angleGardien=0.):
        Strategy.__init__(self,"Attaquant")
        self.dictST = {'alpha': alpha, 'beta': beta, 'angleDribble': angleDribble, 'powerDribble': powerDribble, 'distShoot': distShoot, 'distDribble': distDribble, 'angleGardien': angleGardien}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            if is_close_goal(me, self.dictST['distShoot']):
                foncer(me, power(self.dictST['alpha'], self.dictST['beta']))
                #return essayerBut(me, self.dictST['alpha'], self.dictST['beta'], self.dictST['angleDribble'], self.dictST['powerDribble'], self.dictST['distDribble'], self.dictST['angleGardien'])
            #return avancerBalle(me, self.dictST['angleDribble'], self.dictST['powerDribble'], self.dictST['distDribble'])
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
        if can_shoot(me):
            if is_in_box(me):
                return foncer(me, fonceurCh1ApprochePower)
            return controler(me, power(me))
        return aller_vers_balle(me)

## Strategie Gardien
class GardienStrategy(Strategy):
    #def __init__(self, tempsI=6, n=6, distInter=15.):
    def __init__(self, tempsI=30.65708396899728, n=0, distInter=27.43754193114671):
    #def __init__(self, tempsI=15.189582048077039, n=0, distInter=27.308626539829262):
        Strategy.__init__(self,"Gardien")
        n = tempsI #TODO ajout ???
        self.dictGK = {'tempsI': tempsI, 'n': n, 'distInter': distInter}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            self.dictGK['n'] = self.dictGK['tempsI'] - 1
            return degager(me)
        if must_intercept_gk(me, self.dictGK['distInter']):
            self.dictGK['n'] -= 1
            #print(self.dictGK['n'])
            if self.dictGK['n'] <= 0 :
                self.dictGK['n'] = self.dictGK['tempsI'] - 1
                return get_empty_strategy()
            return intercepter_balle(me,self.dictGK['n'])
        return aller_vers_cage(me)

## Strategie Gardien
class GardienPrecStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Gardien")
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
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
        if can_shoot(me):
            return degager_solo(me)
        if is_in_radius_action(me, me.my_pos, 35.):
            return aller_vers_balle(me)
        return aller_vers_cage(me)
