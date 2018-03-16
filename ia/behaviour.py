# -*- coding: utf-8 -*-
from __future__ import print_function
from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT, maxPlayerShoot, maxPlayerAcceleration, \
        ballBrakeConstant, playerBrackConstant
from .tools import Wrapper, StateFoot, normalise_diff, coeff_friction, is_upside, free_continue, nearest_ball, get_empty_strategy, shootPower
from .conditions import profondeurDegagement, largeurDegagement, empty_goal, is_close_goal
from math import acos, exp, atan, atan2, sin, cos
import random

distMaxFonceurCh1Shoot = GAME_WIDTH/3.
distMaxFonceurNormShoot = GAME_WIDTH/4.
fonceurCh1ApprochePower = 2.65
fonceurCh1HPPower = 4.6
fonceur100Power = 6.
fonceurHPPower = 4.3
controlPower = 1.2

def beh_fonceurNormal(state):
    if is_close_goal(state,distMaxFonceurNormShoot):
        return fonceurHPPower
    return fonceur100Power

def beh_fonceurChallenge1(state):
    if is_close_goal(state,distMaxFonceurCh1Shoot):
        return fonceurCh1HPPower
    return fonceurCh1ApprochePower

def beh_fonceur(state, shooter="normal"):
    if shooter == "ch1":
        return beh_fonceurChallenge1(state)
    return beh_fonceurNormal(state)

def power(dribble):
    CONTROL = 0.98
    DRIBBLE = 0.47#TODO
    if dribble:
        return DRIBBLE
    return CONTROL

def goWith(acceleration):
    """
    Se deplace avec cette acceleration
    """
    return SoccerAction(acceleration)

def goTo(state, dest):
    """
    Se deplacer vers cette destination
    """
    return goWith(normalise_diff(state.my_pos, dest, maxPlayerAcceleration))

def goToBall(state):
    """
    Se deplace vers la balle
    """
    return goTo(state, state.ball_pos)

def goToMyGoal(state):
    """
    Se deplace vers sa cage
    """
    return goTo(state, state.my_goal)

def kickAt(state,dest,powerShoot=maxPlayerShoot):
    """
    Frappe la balle en direction de dest avec
    une puissance de powerShoot
    """
    return SoccerAction(Vector2D(),normalise_diff(state.ball_pos, dest, powerShoot))

def shoot(state, power):
    """
    Fait un tir droit au but
    """
    return kickAt(state,state.opp_goal,power)

def control(state, powerControl=controlPower):#TODO changer le controle pour avancer dans les cotes
    """
    Avance avec la balle au pied
    """
    return kickAt(state,state.opp_goal,powerControl)

def dribble(state, opp, angleDribble, powerDribble, coeffAD):
    """
    Fait un dribble avec une direction aleatoire
    soit vers l'axe, soit vers l'un des deux cotes
    """
    destDribble = Vector2D()
    oPos = opp.position
    angle = atan2(oPos.y-state.my_pos.y,oPos.x-state.my_pos.x)
    try:
        theta = atan((abs(oPos.y-state.my_pos.y) / abs(oPos.x-state.my_pos.x)))/acos(0.)
    except ZeroDivisionError:
        theta = 1.
    rand = exp(-coeffAD*theta)/2.
    quad = state.quadrant
    if random.random() < rand: # mauvais angle (vers un cote)
        if quad == "II" or quad == "IV":
            angleDribble = -angleDribble
    else: # bon angle (vers l'axe)
        if quad == "I" or quad == "III":
            angleDribble = -angleDribble
    angle += angleDribble
    destDribble.x = cos(angle)
    destDribble.y = sin(angle)
    return kickAt(state,state.ball_pos + destDribble,powerDribble)

def goForwardsMF(state, angleDribble, powerDribble, rayDribble, coeffAD, powerControl):
    """
    Essaye d'avance sur le milieu de terrain
    avec la balle et dribble lorsqu'il y a
    un adversaire en face
    """
    can_continue = free_continue(state, state.opponents, rayDribble)
    if can_continue == True:
        return control(state, powerControl)
    return dribble(state, can_continue, angleDribble, powerDribble, coeffAD)

def goForwardsPA(strat, state, alpha, beta, angleDribble, powerDribble, rayDribble, angleGardien, coeffAD, powerControl, distShoot):
    """
    Dans la zone d'attaque, essaye de se
    rapprocher davantage de la surface de
    reparation pour frapper et dribble
    l'adversaire en face de lui
    """
    can_continue = free_continue(state, state.opponents, rayDribble)
    if can_continue == True or empty_goal(strat, state, can_continue, angleGardien):
        if is_close_goal(state, distShoot):
            return shoot(state, shootPower(state, alpha, beta))
        else:
            return control(state, powerControl)
    return dribble(state,can_continue,angleDribble, powerDribble, coeffAD)

def clear_solo(state):
    """
    Degage la balle avec une profondeur
    profondeurDegagement et une largeur
    largeurDegagement
    """
    ecart_x = profondeurDegagement
    if not state.is_team_left(): ecart_x = -ecart_x
    x = state.my_pos.x + ecart_x
    ecart_y = largeurDegagement
    if not is_upside(state.my_pos,state.nearest_opp.position):  ecart_y = -ecart_y
    y = state.my_pos.y + ecart_y
    return kickAt(state,Vector2D(x,y), maxPlayerShoot)

def clear(state, profondeur, largeur, powerDegage=maxPlayerShoot):
    """
    Degage la balle vers son premier
    coequipier
    """
    tm = state.teammates[0]
    ecart_x = profondeur
    if not state.is_team_left(): ecart_x = -ecart_x
    ecart_y = largeur
    if tm.position.y < state.center_spot.y:  ecart_y = -ecart_y
    dec = Vector2D(ecart_x, ecart_y)
    return kickAt(state,dec + state.center_spot, powerDegage)

def shiftAside(state, decalX, decalY):
    """
    Se decale lateralement pour avoir
    une meilleure reception de la balle
    """
    opp = nearest_ball(state, state.opponents)
    ecart_y = decalY
    if is_upside(opp,state.center_spot):  ecart_y = -ecart_y
    ecart_x = decalX
    if state.is_team_left(): ecart_x = -ecart_x
    dec = Vector2D(ecart_x,ecart_y)
    return goTo(state, dec + state.center_spot)

def pushUp(state):
    """
    Monte dans le terrain pour proposer
    des possibilites de passe aux
    coequipiers
    """
    tm = state.teammates[0]
    dest = Vector2D()
    dest.x = tm.position.x
    dest.y = tm.position.y - state.height/2.
    if dest.y < 0:
        dest.y += state.height
    return goTo(state, dest)

def cutDownAngle(state, raySortie):
    """
    Sort de la cage pour reduire
    l'angle de frappe a l'attaquant
    adverse
    """
    trajectoire = state.my_goal
    diff = state.ball_pos - trajectoire
    diff.norm = raySortie
    trajectoire += diff
    return goTo(state,trajectoire)

def try_interception(state, dico):
    """
    Essaye d'intercepter la balle
    s'il lui reste de temps,
    reinitialise son compteur et
    rest immobile sinon
    """
    dico['n'] -= 1
    if dico['n'] <= 0 :
        dico['n'] = dico['tempsI'] - 1
        return get_empty_strategy()
    return intercept_ball(state, dico['n'])

def intercept_ball(state,n):
    """
    Se deplace en vue d'intercepter
    la balle pour une estimation
    de n instants de temps
    """
    # n = 10
    v = state.my_speed
    r = state.my_pos
    vb = state.ball_speed
    rb = state.ball_pos
    fb = ballBrakeConstant
    fj = playerBrackConstant
    coeffb = coeff_friction(n,fb)
    coeffj = coeff_friction(n,fj)
    ax = fj*(rb.x-r.x + vb.x*coeffb-v.x*coeffj)/(n-coeffj)
    ay = fj*(rb.y-r.y + vb.y*coeffb-v.y*coeffj)/(n-coeffj)
    return goWith(Vector2D(ax,ay))
