from soccersimulator import Strategy, Vector2D, GAME_WIDTH, GAME_HEIGHT
from .tools import StateFoot,  get_empty_strategy
from .conditions import must_intercept_gk, can_shoot, is_close_ball
from .behaviour import dribbler, foncer, degager_solo, aller_vers_balle, aller_dest, aller_vers_cage, intercepter_balle, forceShoot, power, essayerBut

class ShootTestStrategy(Strategy):
    def __init__(self, dist=None, alpha=None, beta=None):
        Strategy.__init__(self,"Shoot")
        self.dist = dist
        self.alpha = alpha
        self.beta = beta
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return foncer(me, forceShoot(me, self.alpha, self.beta))

class GardienTestStrategy(Strategy):
    def __init__(self, n=None, distance=None):
        Strategy.__init__(self,"GardienTest")
        self.n_deb = n
        self.n = n
        self.distance = distance
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            self.n = self.n_deb -1
            return degager_solo(me)
        if must_intercept_gk(me, self.distance):
            self.n -= 1
            #print(self.n)
            if self.n <= 0 :
                return get_empty_strategy()
            return intercepter_balle(me,self.n)
        return aller_vers_cage(me)

class ControlerTestStrategy(Strategy):
    def __init__(self, power=None):
        Strategy.__init__(self,"ControlerTest")
        self.power = power
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return controler(me, self.power)
        if is_close_ball(me):
            return get_empty_strategy()
        return aller_vers_balle(me)

class DribblerTestStrategy(Strategy):
    def __init__(self, theta=None, power=None):
        Strategy.__init__(self,"DribblerTest")
        self.alpha = 0.2
        self.beta = 0.7
        self.theta = theta
        self.power = power
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if can_shoot(me):
            return essayerBut(me, self.alpha, self.beta, self.theta, self.power)
        if is_close_ball(me):
            return get_empty_strategy()
        return aller_vers_balle(me)

class TestAccStrategy(Strategy):
    def __init__(self, dist):
        Strategy.__init__(self,"TestAcc")
        self.dist = dist
    def compute_strategy(self,state,id_team,id_player):
        vect = Vector2D(GAME_WIDTH*0.1+self.dist,GAME_HEIGHT/2.)
        me = StateFoot(state,id_team,id_player)
        if me.my_pos.x >= vect.x: 
            print("0")
            return get_empty_strategy()
        print("1")
        return aller_dest(me, vect)
