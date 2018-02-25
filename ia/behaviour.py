from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT, maxPlayerShoot, maxPlayerAcceleration, \
        ballBrakeConstant
from .tools import Wrapper, StateFoot, normalise_diff, coeff_vitesse_reduite, is_upside
from .conditions import high_precision_shoot, profondeurDegagement, largeurDegagement
from math import acos, exp

distMaxFonceurCh1Shoot = GAME_WIDTH/3.
distMaxFonceurNormShoot = GAME_WIDTH/4.
fonceurCh1ApprochePower = 2.65
fonceurCh1HPPower = 4.6
fonceur100Power = 6.
fonceurHPPower = 4.3
dribblePower = 1.2

def shoot(state,dest,puissance=maxPlayerShoot):
    return SoccerAction(Vector2D(),normalise_diff(state.ball_pos, dest, puissance))

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
    return shoot(state,state.opp_goal,power)

def power(state):
    LONG_DRIBBLE = 0.98
    SHORT_DRIBBLE = 0.97
    if state.distance(state.opp_goal) < 50.:
        return SHORT_DRIBBLE
    return LONG_DRIBBLE

def dribbler(state, power=dribblePower):
    return shoot(state,state.opp_goal,power)

def degager_solo(state):
    ecart_x = profondeurDegagement
    if not state.is_team_left(): ecart_x = -ecart_x 
    x = state.my_pos.x + ecart_x
    ecart_y = largeurDegagement
    if not is_upside(state,state.nearest_opp.position):  ecart_y = -ecart_y
    y = state.my_pos.y + ecart_y
    return shoot(state,Vector2D(x,y), maxPlayerShoot)

def degager(state):
    tm = state.tt()[0]
    ecart_x = profondeurDegagement - 15.
    if not state.is_team_left(): ecart_x = -ecart_x 
    ecart_y = largeurDegagement
    if tm.position.y < state.center_point.y:  ecart_y = -ecart_y
    dec = Vector2D(ecart_x, ecart_y)
    return shoot(state,dec + state.center_point, maxPlayerShoot)

def decaler(state):
    ecart_x = profondeurDegagement
    if state.is_team_left(): ecart_x = -ecart_x 
    ecart_y = largeurDegagement
    if not is_upside(state,state.center_point):  ecart_y = -ecart_y
    dec = Vector2D(ecart_x,ecart_y)
    return aller_dest(state, dec + state.center_point)

def aller_acc(acc):
    return SoccerAction(acc)

def aller_acc_2(acc):
    return aller_acc(normalise_diff(Vector2D(),acc,maxPlayerAcceleration))

def aller_dest(state,dest):
    return aller_acc(normalise_diff(state.my_pos, dest, maxPlayerAcceleration))

def aller_vers_balle(state):
    return aller_dest(state,state.ball_pos)

def aller_vers_cage(state):
    return aller_dest(state,state.my_goal)

def intercepter_balle(state,n):
    # n = 10
    v = state.my_speed
    r = state.my_pos
    vb = state.ball_speed
    rb = state.ball_pos
    fc = ballBrakeConstant
    coeff = coeff_vitesse_reduite(n,fc)
    ax = -fc*((v.x-vb.x)*coeff+r.x-rb.x)/(n-coeff)
    ay = -fc*((v.y-vb.y)*coeff+r.y-rb.y)/(n-coeff)
    return aller_acc(Vector2D(ax,ay))


def force(state, alpha, beta):
    vect = Vector2D(-1.,0.)
    u = state.opp_goal - state.my_pos
    dist = u.norm 
    theta = acos((vect.dot(u))/(u.norm*vect.norm))/acos(0.)
    return maxPlayerShoot*(1.-exp(-(alpha*dist)))*exp(-beta*theta)
