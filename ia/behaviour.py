# -*- coding: utf-8 -*-
from __future__ import print_function
from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT, maxPlayerShoot, maxPlayerAcceleration, \
        ballBrakeConstant, playerBrackConstant
from .tools import Wrapper, StateFoot, normalise_diff, coeff_vitesse_reduite, is_upside, free_continue, nearest_ball
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
    try:
        theta = atan((abs(oPos.y-state.my_pos.y) / abs(oPos.x-state.my_pos.x)))/acos(0.)
    except ZeroDivisionError:
        theta = 1.
    rand = exp(-coeffAD*theta)/2.
    quad = state.quadrant()
    if random.random() < rand:
        # mauvais angle (trop proche de la ligne des cages)
        if quad == "II" or quad == "IV":
            #print('negatif',end=' ')
            angleDribble = -angleDribble
        #else:
            #print('positif',end=' ')
    else:
        # bon angle
        if quad == "I" or quad == "III":
            #print('negatif',end=' ')
            angleDribble = -angleDribble
        #else:
            #print('positif',end=' ')
    angle += angleDribble
    #print(angle)
    destDribble.x = cos(angle)
    destDribble.y = sin(angle)
    return shoot(state,state.ball_pos + destDribble,powerDribble)

def avancerBalle(state, angleDribble, powerDribble, rayDribble, coeffAD, powerControl):
    can_continue = free_continue(state, state.opponents(), rayDribble)
    if can_continue == True:
        return controler(state, powerControl)#0.98) #power(False)
    return dribbler(state, can_continue, angleDribble, powerDribble, coeffAD) #power(True)

def essayerBut(strat, state, alpha, beta, angleDribble, powerDribble, rayDribble, angleGardien, coeffAD, powerControl, distShoot):
    can_continue = free_continue(state, state.opponents(), rayDribble)
    if can_continue == True or empty_goal(strat, state, can_continue, angleGardien):
        if is_close_goal(state, distShoot):
            return foncer(state, forceShoot(state, alpha, beta))
        else:
            return controler(state, powerControl)#0.98)
    return dribbler(state,can_continue,angleDribble, powerDribble, coeffAD) #power(True)

def degager_solo(state):
    ecart_x = profondeurDegagement
    if not state.is_team_left(): ecart_x = -ecart_x 
    x = state.my_pos.x + ecart_x
    ecart_y = largeurDegagement
    if not is_upside(state.my_pos,state.nearest_opp.position):  ecart_y = -ecart_y
    y = state.my_pos.y + ecart_y
    return shoot(state,Vector2D(x,y), maxPlayerShoot)

def degager(state, profondeur, ampleur):
    tm = state.teammates()[0]
    ecart_x = profondeur#profondeurDegagement - 15.
    if not state.is_team_left(): ecart_x = -ecart_x 
    ecart_y = ampleur#largeurDegagement
    if tm.position.y < state.center_point.y:  ecart_y = -ecart_y
    dec = Vector2D(ecart_x, ecart_y)
    return shoot(state,dec + state.center_point, maxPlayerShoot)

def decaler(state, decalX, decalY):
    opp = nearest_ball(state, state.opponents())
    ecart_y = decalY#largeurDegagement
    if is_upside(opp,state.center_point):  ecart_y = -ecart_y
    ecart_x = decalX#profondeurDegagement
    if state.is_team_left(): ecart_x = -ecart_x 
    dec = Vector2D(ecart_x,ecart_y)
    return aller_dest(state, dec + state.center_point)

def monterTerrain(state):
    tm = state.teammates()[0]
    dest = Vector2D()
    dest.x = tm.position.x
    dest.y = tm.position.y - state.height/2.
    if dest.y < 0:
        dest.y += state.height
    return aller_dest(state, dest)

def defendre_SR(state, raySortie):
    """oppListe = state.opponents()
    distMin = 5.
    opp = None
    for o in oppListe:
        if state.distance_ball(o.position) < distMin:
            opp = o.position
            print('yes')
            break
    """
    opp = state.ball_pos
    trajectoire = state.my_goal
    if opp is not None:
        diff = opp - state.my_goal
        diff.norm = raySortie
        trajectoire += diff
    return aller_dest(state,trajectoire)

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

def intercepter_balle(strat, state,n):
    # n = 10
    v = state.my_speed
    r = state.my_pos
    vb = state.ball_speed
    rb = state.ball_pos
    fb = ballBrakeConstant
    fj = playerBrackConstant
    coeffb = coeff_vitesse_reduite(n,fb)
    coeffj = coeff_vitesse_reduite(n,fj)
    ax = fj*(rb.x-r.x + vb.x*coeffb-v.x*coeffj)/(n-coeffj)
    ay = fj*(rb.y-r.y + vb.y*coeffb-v.y*coeffj)/(n-coeffj)
    nouv = Vector2D(ax, ay)
    #prec = Vector2D()
    #if hasattr(strat, 'accPrec'):
    #    prec = strat.accPrec
    #nouv = nouv - prec
    #strat.accPrec = nouv
    return aller_acc(nouv)#aller_acc(Vector2D(ax,ay))


def forceShoot(state, alphaShoot, betaShoot):
    vect = Vector2D(-1.,0.)
    u = state.opp_goal - state.my_pos
    dist = u.norm 
    theta = acos(abs(vect.dot(u))/u.norm)/acos(0.)
    return maxPlayerShoot*(1.-exp(-(alphaShoot*dist)))*exp(-betaShoot*theta)
