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
    def __init__(self, alpha=0.2, beta=0.7, angle=0., powerDribble=6., distShoot=27., distDribble=10.):
        Strategy.__init__(self,"Attaquant")
        self.dictST = {'alpha': alpha, 'beta': beta, 'angle': angle, 'powerDribble': powerDribble, 'distShoot': distShoot}
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            if is_close_goal(me, self.dictST['distShoot']):
                return essayerBut(me, self.dictST['alpha'], self.dictST['beta'], self.dictST['angle'], self.dictST['powerDribble'], self.dictST['distDribble'])
            return avancerBalle(me, self.dictST['angle'], self.dictST['powerDribble'], self.dictST['distDribble'])
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
    def __init__(self, tempsI=6, n=6, distInter=15.):
        Strategy.__init__(self,"Gardien")
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
            return degager_solo(me)
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
