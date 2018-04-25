# -*- coding: utf-8 -*-
from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import maxPlayerShoot, maxPlayerAcceleration, \
    ballBrakeConstant, playerBrackConstant
from .tools import normalise_diff, coeff_friction, is_upside, nearest_defender, \
    shootPower, passPower, get_oriented_angle, distance_horizontale, nearest_state, \
    delete_teammate, distance_verticale, is_in_radius_action, nearest_defender_def
from .conditions import is_close_goal, free_teammate, must_advance, is_defensive_zone, \
    must_pass_ball, had_ball_control, must_assist, free_opponent, is_close_ball, \
    ball_advances, is_under_pressure, has_ball_control, both_must_kick, must_intercept
from math import acos, exp, atan2, atan
import random

def beh_fonceurNormal(state):
    distMaxFonceurNormShoot = state.width/4.
    fonceur100Power = 6.
    fonceurHPPower = 4.3
    if is_close_goal(state, distMaxFonceurNormShoot):
        return fonceurHPPower
    return fonceur100Power

def beh_fonceurChallenge1(state):
    distMaxFonceurCh1Shoot = state.width/3.
    fonceurCh1ApprochePower = 2.65
    fonceurCh1HPPower = 4.6
    if is_close_goal(state, distMaxFonceurCh1Shoot):
        return fonceurCh1HPPower
    return fonceurCh1ApprochePower

def beh_fonceur(state, shooter="normal"):
    if shooter == "ch1":
        return beh_fonceurChallenge1(state)
    return beh_fonceurNormal(state)

def goWith(acceleration):
    """
    Se deplace avec comme acceleration <acceleration>
    """
    return SoccerAction(acceleration)

def goTo(state, dest):
    """
    Se deplacer vers <dest>
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

def kickAt(state, dest, powerShoot=maxPlayerShoot):
    """
    Frappe la balle en direction de <dest> avec
    une puissance de <powerShoot>
    """
    return SoccerAction(Vector2D(), normalise_diff(state.ball_pos, dest, powerShoot))

def shoot(state, power):
    """
    Fait un tir droit vers le centre de
    la cage adverse
    """
    return kickAt(state, state.opp_goal, power)

def parallelControl(state, powerControl):
    """
    Avance avec la balle au pied parallelement
    a la ligne de touche
    """
    return kickAt(state, state.ball_pos + state.attacking_vector, powerControl)

def goalControl(state, powerControl):
    """
    Avance avec la balle au pied en direction
    vers le centre de la cage adverse
    """
    return shoot(state, powerControl)

def control(state, powerControl=1.04):
    """
    Avannce avec la balle au pied avec
    une direction dependant de la position
    du joueur sur le terrain
    """
    if distance_horizontale(state.my_pos, state.opp_goal) < 40.:
        return goalControl(state, powerControl)
    return parallelControl(state, powerControl)

def dribble_prec(state, opp, angleDribble, powerDribble, coeffAD):
    """
    Fait un dribble avec une direction aleatoire
    soit vers l'axe, soit vers l'un des deux cotes
    """
    coeffAD=1.305
    oPos = opp.position
    angle = atan2(oPos.y-state.my_pos.y,oPos.x-state.my_pos.x)
    try:
        theta = atan((abs(oPos.y-state.my_pos.y) / abs(oPos.x-state.my_pos.x)))/acos(0.)
    except ZeroDivisionError:
        theta = 1.
    rand = exp(-coeffAD*theta)/2.
    quad = state.quadrant
    if random.random() < rand: # mauvais angle (vers l'adversaire)
        if quad == "II" or quad == "IV":
            angleDribble = -angleDribble
    else: # bon angle (vers la cage adverse)
        if quad == "I" or quad == "III":
            angleDribble = -angleDribble
    angle += angleDribble
    destDribble = Vector2D(angle=angle, norm=1.)
    return kickAt(state, state.ball_pos + destDribble, powerDribble)

def dribble(state, opp, angleDribble, powerDribble, coeffAD):
    """
    Fait un dribble avec une direction aleatoire
    soit vers l'axe, soit vers l'un des deux cotes
    """
    me_opp = (opp.position - state.my_pos).normalize()
    me_goal = state.attacking_vector
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
    destDribble = Vector2D(angle=angle, norm=1.)
    return kickAt(state, state.ball_pos + destDribble, powerDribble)

def passBall(state, tm, powerPasse, thetaPasse, coeffPushUp):
    """
    Fait une passe vers <tm>
    """
    dest = tm.position
    vitesse = tm.vitesse.copy().normalize()
    if vitesse.dot(state.attacking_vector) < 0.:
        vitesse = (-0.5) * vitesse
    dest += coeffPushUp*vitesse
    return kickAt(state, dest, passPower(state, dest, powerPasse, thetaPasse))

def loseMark(state, rayPressing, distDemar, angleInter):
    """
    Se demarque de l'adversaire le plus proche
    s'il y en a un a distance <rayPressing>,
    se decale sinon
    """
    opp = state.nearest_opponent(rayPressing)
    if opp is None:
        return shiftAside(state, distDemar, angleInter)
    return shiftAsideMark(state, opp, distDemar)

def mark(state, opp, distMar):
    """
    Se positionne a une distance <distMar>
    de <opp> tout en lui bloquant la trajectoire
    de reception de la balle
    """
    vect = (state.ball_pos - opp.position).normalize()
    vect.norm = distMar
    return goTo(state, opp.position + vect)

def shiftAside(state, distDemar, angleInter):
    """
    Se positionne a une distance <distDemar> de
    l'adversaire le plus proche de la balle pour
    avoir une meilleure possibilite de reception
    de la balle
    """
    opp = state.opponent_nearest_ball
    while True:
        dest = Vector2D.create_random(low=-1, high=1)
        dest.norm = distDemar
        dest += state.ball_pos
        if state.is_valid_position(dest) and state.free_trajectory(dest, angleInter) and \
           distance_horizontale(dest, state.my_goal) > distance_horizontale(opp.position, state.my_goal)-5.:
            break
    return goTo(state, dest)

def shiftAsideMark(state, opp, distDemar):
    """
    Se positionne a une distance <distDemar> de
    <opp>
    """
    dest = None
    while True:
        dest = Vector2D.create_random(low=-1, high=1)
        dest.norm = distDemar
        dest += opp.position
        if state.is_valid_position(dest) and \
           distance_horizontale(dest, state.my_goal) > 10.+distance_horizontale(opp.position, state.my_goal):
            break
    return goTo(state, dest)

def goForwardsPASolo(state, dico):
    """ 1v1
    Dans la zone d'attaque, essaye de se
    rapprocher davantage de la surface de
    reparation pour frapper et dribble
    l'adversaire en face de lui
    """
    oppDef = nearest_defender(state, state.opponents, dico['rayDribble'])
    if oppDef is None:
        if is_close_goal(state, dico['distShoot']) and \
           state.free_trajectory(state.opp_goal, dico['angleInter']):
            return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
        return control(state, dico['controleAttaque'])
    return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])

def goForwardsMFSolo(state, dico):
    """ 1v1
    Essaye d'avance sur le milieu de terrain
    avec la balle et dribble lorsqu'il y a
    un adversaire en face
    """
    oppDef = nearest_defender(state, state.opponents, dico['rayDribble'])
    if oppDef is None:
        return control(state, dico['controleMT'])
    return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])

def goForwardsPA(state, dico):
    """ 2v2/4v4
    Dans la zone d'attaque, essaye de se
    rapprocher davantage de la surface de
    reparation pour frapper et dribble
    l'adversaire en face de lui
    """
    if is_close_goal(state, dico['distShoot']/2.) and \
       state.free_trajectory(state.opp_goal, 2*dico['angleInter']/3):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    oppDef = nearest_defender(state, state.opponents, dico['rayDribble'])
    tm = free_teammate(state, dico['angleInter'])
    if oppDef is not None:
        if tm is not None:
            if is_close_goal(state, dico['distShoot']) and \
               must_assist(state, tm, dico['angleInter'], dico['coeffPushUp']/2.):
                return passBall(state,tm,dico['powerPasse'],dico['thetaPasse'],dico['coeffPushUp']/2.)+\
                    pushUp(state, dico['coeffPushUp'])
            if must_pass_ball(state, tm, dico['angleInter']):
                return passBall(state,tm,dico['powerPasse'],dico['thetaPasse'],dico['coeffPushUp'])+\
                    pushUp(state, dico['coeffPushUp'])
        return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])
    return control(state, dico['controleAttaque'])

def goForwardsMF(state, dico):
    """ 2v2/4v4
    Essaye d'avance sur le milieu de terrain
    avec la balle et dribble lorsqu'il y a
    un adversaire en face
    """
    oppDef = nearest_defender(state, state.opponents, dico['rayDribble'])
    if oppDef is not None:
        tm = free_teammate(state, dico['angleInter'])
        if tm is not None and must_pass_ball(state, tm, dico['angleInter']):
            return passBall(state, tm, dico['powerPasse'], dico['thetaPasse'], dico['coeffPushUp'])+\
                pushUp(state, dico['coeffPushUp'])
        return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])
    return control(state, dico['controleMT'])

def goForwardsDef(state, dico):
    """
    Essaye d'avancer dans la zone defensive
    avec la balle et fait une passe passe ou
    un degagement lorsqu'il y a un
    adversaire en face
    """
    angleInter = 5.*dico['angleInter']/4.
    #angleInter = dico['angleInter']
    oppDef = nearest_defender_def(state, state.opponents, dico['rayDribble'])
    if oppDef is not None:
        tm = free_teammate(state, angleInter)
        if tm is not None and must_pass_ball(state, tm, angleInter) \
           and not is_under_pressure(state, tm, dico['rayPressing']):
            return passBall(state, tm, dico['powerPasse'], dico['thetaPasse'], dico['coeffPushUp'])+\
                pushUp(state, dico['coeffPushUp'])
        return clear(state, angleClear=1.2)
    return control(state, dico['controleMT'])

def clearSolo(state):
    """
    Degage la balle avec une trajectoire
    horizontale a partir de la position 
    de la balle vers la cage adverse
    """
    return kickAt(state, state.attacking_vector + state.ball_pos, 4.)

def clear(state, angleClear=1., power=3.5):
    """
    Fait une ouverture d'un certain
    angle par rapport a l'adversaire
    le plus proche de la balle
    """
    opp = state.opponent_nearest_ball
    me_opp = (opp.position - state.ball_pos).normalize()
    angle = atan2(me_opp.y,me_opp.x)
    if state.is_team_left():
        if is_upside(opp.position, state.ball_pos):
            angleClear = -angleClear
    else:
        if is_upside(state.ball_pos, opp.position):
            angleClear = -angleClear
    angle += angleClear
    destClear = Vector2D(angle=angle, norm=10.)
    return kickAt(state, state.ball_pos + destClear, power)

def pushUp(state, coeffPushUp):
    """
    Monte dans le terrain pour proposer
    une possibilite de passe aux
    coequipiers
    """
    if state.numPlayers == 4:
        return pushUp4v4(state, coeffPushUp)
    return pushUp2v2(state, coeffPushUp)

def pushUp4v4(state, coeffPushUp):
    """
    C.f. pushUp
    Specifique au 4v4
    """
    porteur = state.nearest_ball(state.teammates)
    tm_list = state.offensive_teammates
    delete_teammate(porteur, tm_list)
    tm = tm_list[0]
    dest = Vector2D()
    dest.x = porteur.position.x + state.my_speed.x*coeffPushUp
    distMoi = distance_verticale(state.my_pos, porteur.position)
    distTM = distance_verticale(tm.position, porteur.position)
    diff = 25.
    entree = -1
    if distMoi < distTM:
        if is_upside(state.my_pos, porteur.position):
            dest.y = porteur.position.y + diff
            entree = 1
            if dest.y >= 90.:
                dest.y = porteur.position.y - diff
        else:
            dest.y = porteur.position.y - diff
            entree = 2
            if dest.y < 0.:
                dest.y = porteur.position.y + diff
    else:
        if is_upside(tm.position, porteur.position):
            if porteur.position.y + diff < 90.:
                if porteur.position.y + 2*diff < 90.:
                    dest.y = porteur.position.y + 2*diff
                else:
                    dest.y = porteur.position.y - diff
            else:
                dest.y = porteur.position.y - 2*diff
        else:
            if porteur.position.y - diff > 0.:
                if porteur.position.y - 2*diff > 0.:
                    dest.y = porteur.position.y - 2*diff
                else:
                    dest.y = porteur.position.y + diff
            else:
                dest.y = porteur.position.y + 2*diff
    return goTo(state, dest)

def pushUp2v2(state, coeffPushUp):
    """
    C.f. pushUp
    Specifique au 2v2
    """
    tm = state.teammates[0]
    dest = Vector2D()
    dest.x = tm.position.x + state.my_speed.x*coeffPushUp
    dest.y = tm.position.y + 30.
    if dest.y > 75.:
        dest.y = tm.position.y - 30.
    return goTo(state, dest)

def cutDownAngle(state, raySortie, rayInter):
    """
    Se positionne sur la trajectoire de
    l'attaquant adverse a une distance
    de <raySortie> de la cage ou a une
    distance de <rayInter> de la balle
    """
    position = state.my_goal
    diff = state.ball_pos - position
    diff.norm = max(raySortie, diff.norm - rayInter)
    position += diff
    return goTo(state,position)

def cutDownAngle_gk(state, raySortie):
    """
    Se positionne sur la trajectoire de
    l'attaquant adverse a une distance
    de <raySortie> de la cage 
    """
    position = state.my_goal
    diff = state.ball_pos - position
    diff.norm = raySortie
    position += diff
    return goTo(state,position)

def cutDownAngle_def(state, raySortie, rayInter):
    """
    Se positionne sur la trajectoire de
    l'attaquant adverse a une distance
    de <raySortie> de la cage 
    """
    position = state.my_goal
    diff = state.ball_pos - position
    diff.norm = max(min(raySortie, diff.norm - rayInter), 20.)
    position += diff
    return goTo(state,position)

def tryInterception(state, dico):
    """
    Essaye d'intercepter la balle
    s'il lui reste du temps,
    reinitialise son compteur et
    se dirige vers la balle sinon
-    """
    if dico['n'] == -1:
        dico['n'] = dico['tempsI']
    dico['n'] -= 1
    if dico['n'] < 0 :
        dico['n'] = dico['tempsI']
        return goToBall(state)
    return interceptBall(state, dico['n']+1)

def interceptBall(state, n):
    """
    Se deplace pour intercepter
    la balle pour une estimation
    de <n> instants de temps
    """
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
