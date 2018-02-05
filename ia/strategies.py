from tools import *


###définir les actions

###def tirer(state):
###    return state.shoot(state.but_dav)

###def dribbler(state):
#    if state.distance()<...:
#        return tirer(state)
#    return petitepasse(satte)


#   def compute_strategy(self,state,idt,idp):
#       mystate =...
#       return tirer(mystate)

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
        return myState.aller_dest(myState.ball_position())

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
            return myState.degager()
            #return myState.shoot(myState.cage_but())
        if myState.doit_intercepter(): #and myState.est_plus_proche(myState.adversaires())""" 
            #return myState.aller_dest(myState.ball_position())
            tempsInterception = interceptionLongue
            if myState.distance_ball_joueur() < distanceInterceptionCourte:
                tempsInterception = interceptionCourte
            return myState.go_to_ball(tempsInterception)
        return myState.aller_dest(myState.ma_cage())
