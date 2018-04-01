# -*- coding: utf-8 -*-
from soccersimulator import Strategy, Vector2D
from .tools import StateFoot, get_empty_strategy, shootPower
from .conditions import must_intercept, has_ball_control, is_close_ball, is_close_goal
from .behaviour import dribble, shoot, clearSolo, goToBall, goTo, goToMyGoal, interceptBall, power, goForwardsPA, control, passBall#, receiveBall

class ShootTestStrategy(Strategy):
    def __init__(self, dist=None, alpha=None, beta=None):
        Strategy.__init__(self,"Shoot")
        self.dist = dist
        self.alpha = alpha
        self.beta = beta
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        return shoot(me, shootPower(me, self.alpha, self.beta))



class GardienTestStrategy(Strategy):
    def __init__(self, n=None, distance=None):
        Strategy.__init__(self,"GardienTest")
        self.n_deb = n
        self.n = n
        self.distance = distance
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            self.n = self.n_deb -1
            return clearSolo(me)
        if must_intercept(me, self.distance):
            self.n -= 1
            #print(self.n)
            if self.n <= 0 :
                return get_empty_strategy()
            return interceptBall(me,self.n)
        return goToMyGoal(me)



class ControlerTestStrategy(Strategy):
    def __init__(self, power=None):
        Strategy.__init__(self,"ControlerTest")
        self.power = power
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return control(me, self.power)
        if is_close_ball(me):
            return get_empty_strategy()
        return goToBall(me)



class DribblerTestStrategy(Strategy):
    def __init__(self, theta=None, power=None):
        Strategy.__init__(self,"DribblerTest")
        self.alpha = 0.2
        self.beta = 0.7
        self.theta = theta
        self.power = power
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            return goForwardsPA(me, self.alpha, self.beta, self.theta, self.power)
        if is_close_ball(me):
            return get_empty_strategy()
        return goToBall(me)



## Strategie PasseTest
"""
C'est un joueur qui essaie toujours d'avancer balle
au pied quand il la possede, sauf s'il est dans
la surface de reparation, ou il tire la balle vers
la cage adverse
"""
class PasseTestStrategy(Strategy):
    def __init__(self, power=3.):
        Strategy.__init__(self,"PasseTest")
        self.power = power
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            if is_close_goal(me, 10.):
                return shoot(me, fonceurCh1ApprochePower)
            return passBall(me, 10., self.power, 0.8)
            #return control(me, power(me))
        #return receiveBall(me, 0.5) pas de commentaire ici !!!
        return goToBall(me)



class TestAccStrategy(Strategy):
    def __init__(self, dist):
        Strategy.__init__(self,"TestAcc")
        self.dist = dist
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        vect = Vector2D(me.width*0.1+self.dist,me.goal_height)
        if me.my_pos.x >= vect.x:
            print("0")
            return get_empty_strategy()
        print("1")
        return goTo(me, vect)


class ReceptionTestStrategy(Strategy):
    def __init__(self, coeff=None):
        Strategy.__init__(self,"ReceptionTest")
        self.coeff = coeff
        self.cont = True
    def compute_strategy(self,state,id_team,id_player):
        me = StateFoot(state,id_team,id_player)
        if has_ball_control(me):
            self.cont = False
            return control(me, self.coeff)
        if self.cont:
            return goToBall(me)
        return get_empty_strategy()
