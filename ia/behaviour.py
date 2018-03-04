from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT, maxPlayerShoot, maxPlayerAcceleration, \
        ballBrakeConstant
from .tools import Wrapper, StateFoot, normalise_diff, coeff_vitesse_reduite, is_upside, free_continue
from .conditions import high_precision_shoot, profondeurDegagement, largeurDegagement, empty_goal, is_close_goal
from math import acos, exp, atan, atan2, sin, cos
import random

distMaxFonceurCh1Shoot = GAME_WIDTH/3.
distMaxFonceurNormShoot = GAME_WIDTH/4.
fonceurCh1ApprochePower = 2.65
fonceurCh1HPPower = 4.6
fonceur100Power = 6.
fonceurHPPower = 4.3
controlPower = 1.2

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

def power(dribble):
    CONTROL = 0.98
    DRIBBLE = 0.47#TODO
    if dribble:
        return DRIBBLE
    return CONTROL

def controler(state, power=controlPower):
    return shoot(state,state.opp_goal,power)

def dribbler(state, opp, angleDribble, powerDribble, coeffAD):
    destDribble = Vector2D()
    oPos = opp.position
    angle = atan2(oPos.y-state.my_pos.y,oPos.x-state.my_pos.x)
    theta = atan((abs(oPos.y-state.my_pos.y) / abs(oPos.x-state.my_pos.x)))/acos(0.)
    rand = exp(-coeffAD*theta)/2.
    quad = state.quadrant()
    if random.random() < rand:
        # mauvais angle (trop proche de la ligne des cages)
        if quad == "II" or quad == "IV":
            angleDribble = -angleDribble
    else:
        # bon angle
        if quad == "I" or quad == "III":
            angleDribble = -angleDribble
    angle += angleDribble
    destDribble.x = cos(angle)
    destDribble.y = sin(angle)
    return shoot(state,state.ball_pos + destDribble,powerDribble)

def avancerBalle(state, angleDribble, powerDribble, distDribble, coeffAD):
    can_continue = free_continue(state, state.opponents(), distDribble)
    if can_continue == True:
        return controler(state, 0.98) #power(False)
    return dribbler(state, can_continue, angleDribble, powerDribble, coeffAD) #power(True)

def essayerBut(state, alpha, beta, angleDribble, powerDribble, distDribble, angleGardien, coeffAD):
    can_continue = free_continue(state, state.opponents(), distDribble)
    if can_continue == True or state.distance(state.opp_goal) < can_continue.position.distance(state.opp_goal):# or empty_goal(state, can_continue, angleGardien):
        if is_close_goal(state):
            return foncer(state, forceShoot(state, alpha, beta))
        else:
            return controler(state, 0.98)
    return dribbler(state,can_continue,angleDribble, powerDribble, coeffAD) #power(True)

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
    ecart_x = profondeurDegagement# - 15.
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


def forceShoot(state, alpha, beta):
    vect = Vector2D(-1.,0.)
    u = state.opp_goal - state.my_pos
    dist = u.norm 
    theta = acos(abs(vect.dot(u))/u.norm)/acos(0.)
    return maxPlayerShoot*(1.-exp(-(alpha*dist)))*exp(-beta*theta)
