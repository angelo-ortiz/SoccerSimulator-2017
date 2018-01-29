from soccersimulator  import Strategy, SoccerAction, Vector2D
from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from soccersimulator.settings import *


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
        player_state = state.player_state(id_team,id_player)
        player_position = state.player_state(id_team,id_player).position
        ecart_player_ball = state.ball.position - player_position
        dist_player_ball = ecart_player_ball.norm
        pos_x = 0. if id_team == 2 else GAME_WIDTH
        goal_milieu = Vector2D(pos_x,GAME_HEIGHT/2.)
        if dist_player_ball <= PLAYER_RADIUS+BALL_RADIUS and player_state.can_shoot():
            acceleration = goal_milieu - state.ball.position
            return SoccerAction(acceleration,acceleration.copy().norm_max(maxPlayerShoot))
        ecart_player_ball.norm_max(maxPlayerAcceleration)
        return SoccerAction(ecart_player_ball)

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
