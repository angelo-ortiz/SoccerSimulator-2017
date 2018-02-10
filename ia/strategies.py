from .tools import *

def shoot(state,dest,puissance):
    return SoccerAction(Vector2D(),normaliser_diff(state.ball_position, dest, puissance))
   
def foncer(state):
    return shoot(state,state.cage_adverse,shootPower)

def dribbler(state):
    return shoot(state,state.cage_adverse,dribblePower)

def degager(state):
    ecart_x = profondeurDegagement
    if not state.is_team_left() : ecart_x = -ecart_x 
    x = state.position.x + ecart_x
    v = state.vitesse
    y = 0. if state.est_en_dessus(state.adversaire_le_plus_proche()) else GAME_HEIGHT
    return shoot(state,Vector2D(x,y), maxPlayerShoot)

def aller_acc(acc):
    return SoccerAction(acc)

def aller_dest(state,dest):
    return aller_acc(dest-state.position)

def aller_vers_balle(state):
    return aller_dest(state,state.ball_position)

def aller_vers_cage(state):
    return aller_dest(state,state.cage)

def intercepter_balle(state,n):
    # n = 10
    v = state.vitesse
    r = state.position
    vb = state.ball_vitesse
    rb = state.ball_position
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
            return foncer(myState)
        return aller_vers_balle(myState)

## Strategie Dribbler
class DribblerStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Dribbler")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if myState.can_shoot():
            return dribbler(myState)
        return aller_vers_balle(myState)

## Strategie Defendre
class DefendreStrategy(Strategy):
    def __init__(self):
        Strategy.__init__(self,"Defendre")
    def compute_strategy(self,state,id_team,id_player):
        myState = StateFoot(state,id_team,id_player)
        if myState.can_shoot():
            return degager(myState)
        if myState.doit_intercepter():
            #return aller_vers_balle()
            tempsInterception = interceptionLongue
            if myState.distance_ball_joueur() < distanceInterceptionCourte:
                tempsInterception = interceptionCourte
            return intercepter_balle(myState,tempsInterception)
        return aller_vers_cage(myState)
