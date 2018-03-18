# -*- coding: utf-8 -*-
from __future__ import print_function
from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT, maxPlayerShoot, maxPlayerAcceleration, \
        ballBrakeConstant, playerBrackConstant
from .tools import Wrapper, StateFoot, normalise_diff, coeff_friction, is_upside, nearest_defender, \
    nearest_ball, get_empty_strategy, shootPower, passPower, get_oriented_angle
from .conditions import profondeurDegagement, largeurDegagement, empty_goal, is_close_goal, free_teammate
from math import acos, exp, atan2, sin, cos
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
    me_opp = (opp.position - state.my_pos).normalize()
    me_goal = (state.opp_goal - state.my_pos).normalize()
    angle = atan2(me_opp.y,me_opp.x)
    theta = get_oriented_angle(me_goal, me_opp)/acos(0.)
    rand = exp(-coeffAD*abs(theta))/2.
    quad = state.quadrant
    if random.random() < rand: # mauvais angle (vers l'adversaire)
        if theta < 0.:
            angleDribble = -angleDribble
    else: # bon angle (vers la cage adverse)
        if theta > 0.:
            angleDribble = -angleDribble
    angle += angleDribble
    destDribble.x = cos(angle)
    destDribble.y = sin(angle)
    return kickAt(state, state.ball_pos + destDribble, powerDribble)

def passBall(state, rayPassePressing, maxPowerPasse, thetaPass):
    """
    Fait une passe vers un coequipier sans
    marquage
    TODO: il faut enlever la recherche du coequipier et plutot
    le passer en parametre => plus de strategie vide
    """
    tm = free_teammate(state, rayPassePressing)
    if tm is None:
        return get_empty_strategy()
    dest = tm
    return kickAt(state, dest, passPower(state, dest, maxPowerPasse, thetaPass))

def receiveBall(state, angleRecept):
    """
    Recoit une passe
    TODO: enlever la strategie vide
    """
    vectBall = (state.my_pos - state.ball_pos).normalize()
    vectSpeed = state.ball_speed.copy().normalize()
    if state.distance(state.ball_pos) <= 10 and vectSpeed.dot(vectBall) <= angleRecept:
        return goToBall(state)
    return get_empty_strategy()

def goForwardsMF(state, angleDribble, powerDribble, rayDribble, coeffAD, powerControl):
    """
    Essaye d'avance sur le milieu de terrain
    avec la balle et dribble lorsqu'il y a
    un adversaire en face
    """
    oppDef = nearest_defender(state, state.opponents, rayDribble)
    if oppDef is None:
        return control(state, powerControl)
    return dribble(state, oppDef, angleDribble, powerDribble, coeffAD)

def goForwardsPA(strat, state, alpha, beta, angleDribble, powerDribble, rayDribble, angleGardien, coeffAD, powerControl, distShoot):
    """
    Dans la zone d'attaque, essaye de se
    rapprocher davantage de la surface de
    reparation pour frapper et dribble
    l'adversaire en face de lui
    """
    oppDef = nearest_defender(state, state.opponents, rayDribble)
    if oppDef is None or empty_goal(strat, state, oppDef, angleGardien):
        if is_close_goal(state, distShoot):
            return shoot(state, shootPower(state, alpha, beta))
        else:
            return control(state, powerControl)
    return dribble(state,oppDef,angleDribble, powerDribble, coeffAD)

def clearSolo(state):
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
    TODO: la positionnement dans le terrain
    est a revoir
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

def tryInterception(state, dico):
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
    return interceptBall(state, dico['n'])

def interceptBall(state,n):
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
