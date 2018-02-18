from .tools import *
from .conditions import *

fonceurCh1ApprochePower = 2.65
fonceurCh1HPPower = 4.6
fonceur100Power = 6.
fonceurHPPower = 4.3
dribblePower = 1.2

def shoot(state,dest,puissance=maxPlayerShoot):
    return SoccerAction(Vector2D(),normaliser_diff(state.ball_position, dest, puissance))

def beh_fonceurNormal(state):
    if high_precision_shoot(state,distMaxFonceurNormShoot):
        return fonceurHPPower
    return fonceur100Power

def beh_fonceurChallenge1(state):
    if high_precision_shoot(state,distMaxFonceurCh1Shoot):
        return fonceurCh1HPPower
    return fonceurCh1ApprochePower

def beh_fonceur(state, shooter="normal"):
    if shooter == "ch1":
        return beh_fonceurChallenge1(state)
    return beh_fonceurNormal(state)

def foncer(state, power):
    return shoot(state,state.cage_adverse,power)

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

def aller_acc_2(acc):
    return aller_acc(normaliser_diff(Vector2D(),acc,maxPlayerAcceleration))

def aller_dest(state,dest):
    return aller_acc(normaliser_diff(state.position, dest, maxPlayerAcceleration))

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
    fc = ballBrakeConstant
    coeff = coeff_vitesse_reduite(n,fc)
    ax = -fc*((v.x-vb.x)*coeff+r.x-rb.x)/(n-coeff)
    ay = -fc*((v.y-vb.y)*coeff+r.y-rb.y)/(n-coeff)
    return aller_acc_2(Vector2D(ax,ay))

