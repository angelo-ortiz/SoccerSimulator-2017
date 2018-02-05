from tools import *

def shoot(state,dest=None,degager=False):
    if not dest: dest = state.cage_adverse
    puissance = accelerationShoot if not degager else maxPlayerShoot
    return SoccerAction(Vector2D(),normaliser_diff(state.ball_position(), dest, puissance))
    
def degager(state):
    ecart_x = profondeurDegagement
    if not state.is_team_left() : ecart_x = -ecart_x 
    x = state.my_position().x + ecart_x
    v = state.my_vitesse()
    y = 0. if state.est_en_dessus(state.adversaire_le_plus_proche()) else GAME_HEIGHT
    return shoot(state,Vector2D(x,y), True)

def aller_acc(acc):
    return SoccerAction(acc)

def aller_dest(state,dest):
    return aller_acc(dest-state.my_position())

def aller_vers_balle(state):
    return aller_dest(state,state.ball_position())

def aller_vers_cage(state):
    return aller_dest(state,state.ma_cage)

def intercepter_balle(state,n):
    # n = 10
    v = state.my_vitesse()
    r = state.my_position()
    vb = state.ball_vitesse()
    rb = state.ball_position()
    #ax = (10*(v.x-vb.x)+r.x-rb.x)/(-50)
    #ay = (10*(v.y-vb.y)+r.y-rb.y)/(-50)
    #ax = 2.*(n*v.x-vb.x*self.coeff_vitesse_reduite(n,ballBrakeConstant)+r.x-rb.x)/(n*n)
    #ay = 2.*(n*v.y-vb.y*self.coeff_vitesse_reduite(n,ballBrakeConstant)+r.y-rb.y)/(n*n)
    fc = ballBrakeConstant
    ax = -fc*((v.x-vb.x)*coeff_vitesse_reduite(n,fc)+r.x-rb.x)/(n-coeff_vitesse_reduite(n,fc))
    ay = -fc*((v.y-vb.y)*coeff_vitesse_reduite(n,fc)+r.y-rb.y)/(n-coeff_vitesse_reduite(n,fc))
    return aller_acc(Vector2D(ax,ay))

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
            return shoot(myState)
        return aller_vers_balle(myState)

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
            return degager(myState)
        if myState.doit_intercepter(): #and myState.est_plus_proche(myState.adversaires())""" 
            #return myState.aller_dest(myState.ball_position())
            tempsInterception = interceptionLongue
            if myState.distance_ball_joueur() < distanceInterceptionCourte:
                tempsInterception = interceptionCourte
            return intercepter_balle(myState,tempsInterception)
        return aller_vers_cage(myState)
