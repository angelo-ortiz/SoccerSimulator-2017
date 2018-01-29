from soccersimulator  import Strategy, SoccerAction, Vector2D
from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from soccersimulator.settings import *

## StateFoot ...
class StateFoot(object):
    def __init__(self,state,id_team,id_player):
        self.state = state
        self.key = (id_team,id_player)
    def my_position(self):
        return self.state.player_state(*self.key).position
    def ball_position(self):
        return self.state.ball.position
    def aller_vers_balle(self):
        p = Vector2D()
        return self.aller(p)
    def aller(self,p):
        return SoccerAction(p-self.my_position())
    def shoot(self,p):
        return SoccerAction(Vector2D(),(p-self.ball_position()).norm_max(3.5))
    def distance_ball(self,p):
        return (self.ball_position()-p).norm
    def distance_ball_joueur(self):
        return self.distance_ball(self.my_position())
    def est_plus_proche(self,p):
        dist_ball_p = self.distance_ball(p)
        return self.distance_ball_joueur() < dist_ball_p
    def adversaire_1v1(self):
        return self.state.player_state(3-self.key[0],0)
    def can_shoot(self):
        dist_ball_joueur = self.distance_ball(self.my_position())
        ball_est_proche = dist_ball_joueur <= PLAYER_RADIUS + BALL_RADIUS
        return ball_est_proche and self.state.player_state(*self.key).can_shoot()
    def cage_but(self):
        return Vector2D(0. if self.key[0] == 2 else GAME_WIDTH,GAME_HEIGHT/2.)
    def ma_cage(self):
        return Vector2D(0. if self.key[0] == 1 else GAME_WIDTH,GAME_HEIGHT/2.)
    def compute_strategy(self):
        #TODO
        return self.aller(p)

## Strategie aleatoire
class RandomStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Random")
    def compute_strategy(self,state,id_team,id_player):
        return SoccerAction(Vector2D.create_random(-1.,1.),Vector2D.create_random(-1.,1.))

## Strategie Fonceur
class FonceurStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Fonceur")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if myState.can_shoot():
            return myState.shoot(myState.cage_but())
        return myState.aller(myState.ball_position())

## Strategie Dribbler
class DribblerStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Dribbler")
    def compute_strategy(self,state,id_team,id_player):
        player_position = state.player_state(id_team,id_player).position
        ecart_player_ball = state.ball.position - player_position
        dist_player_ball = ecart_player_ball.norm
        pos_x = 0. if id_team == 2 else GAME_WIDTH
        goal_milieu = Vector2D(pos_x,GAME_HEIGHT/2.)
        if dist_player_ball <= PLAYER_RADIUS+BALL_RADIUS:
            acceleration = goal_milieu - state.ball.position
            return SoccerAction(acceleration,acceleration.copy().norm_max(maxPlayerShoot/2.))
        ecart_player_ball.norm = maxPlayerAcceleration
        return SoccerAction(ecart_player_ball)

## Strategie Defendre
class DefendreStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Defendre")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if myState.can_shoot():
            return myState.shoot(myState.cage_but())
        if myState.est_plus_proche(myState.adversaire_1v1().position):
            return myState.aller(myState.ball_position())
        return myState.aller(myState.ma_cage())
