# -*- coding: utf-8 -*-
from __future__ import print_function
from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT, maxPlayerShoot, maxPlayerAcceleration, \
    ballBrakeConstant, playerBrackConstant
from .tools import Wrapper, StateFoot, normalise_diff, coeff_friction, is_upside, nearest_defender, \
    nearest_ball, get_empty_strategy, shootPower, passPower, get_oriented_angle, distance_horizontale, \
    nearest_state, delete_teammate, distance_verticale, is_in_radius_action, nearest_defender_def
from .conditions import empty_goal, is_close_goal, free_teammate, must_advance, is_defensive_zone, \
    must_pass_ball, had_ball_control, must_assist, free_opponent, is_close_ball, ball_advances, \
    is_under_pressure, has_ball_control, both_must_kick, must_intercept
from math import acos, exp, atan2, sin, cos, atan
import random

def beh_fonceurNormal(state):
    distMaxFonceurNormShoot = GAME_WIDTH/4.
    fonceur100Power = 6.
    fonceurHPPower = 4.3
    if is_close_goal(state,distMaxFonceurNormShoot):
        return fonceurHPPower
    return fonceur100Power

def beh_fonceurChallenge1(state):
    distMaxFonceurCh1Shoot = GAME_WIDTH/3.
    fonceurCh1ApprochePower = 2.65
    fonceurCh1HPPower = 4.6
    if is_close_goal(state,distMaxFonceurCh1Shoot):
        return fonceurCh1HPPower
    return fonceurCh1ApprochePower

def beh_fonceur(state, shooter="normal"):
    if shooter == "ch1":
        return beh_fonceurChallenge1(state)
    return beh_fonceurNormal(state)

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

def bestShoot(state, power):
    """
    Fait un tir droit au but
    """
    dest = state.opp_goal
    if random.random() < 0.5:
        dest.y += 5.
    else:
        dest.y -= 5.
    return kickAt(state,dest,power)

def parallelControl(state, powerControl):
    """
    Avance avec la balle au pied parallelement
    a la ligne de touche
    """
    return kickAt(state,state.ball_pos + state.attacking_vector,powerControl)

def goalControl(state, powerControl):
    """
    Avance avec la balle au pied parallelement
    a la ligne de touche
    """
    return shoot(state,powerControl)

def control(state, powerControl=1.04):
    """
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
    #me_goal = (state.opp_goal - state.my_pos).normalize()
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

def passBall(state, dest, powerPasse, thetaPasse, coeffPushUp):
    """
    Fait une passe vers un coequipier sans
    marquage
    """
    destp = dest.position
    vitesse = dest.vitesse.copy().normalize()
    if vitesse.dot(state.attacking_vector) < 0.:
        vitesse = (-0.5) * vitesse
    destp += coeffPushUp*vitesse
    return kickAt(state, destp, passPower(state, destp, powerPasse, thetaPasse))

def passiveSituationSolo(state, dico):
    """
    Quand le joueur n'a pas le controle sur
    la balle:
    - si la balle approche il s'approche pour
    recevoir la balle
    - s'il est le joueur le plus proche de la
    balle ou s'il vient de faire un dribble/controle
    il se dirige de nouveau vers la balle
    - si un coequipier a franchi une distance
    avec la balle, il monte de le terrain
    pour lui proposer des solutions
    - sinon il se decale lateralement
    """
    if state.is_nearest_ball() or had_ball_control(state, dico['rayReprise'], dico['angleReprise']):
        return tryInterception(state, dico)
    if is_close_goal(state, dico['distAttaque']) and ball_advances(state):
        return tryInterception(state, dico)
    if must_intercept(state, dico['rayInter']):
        return tryInterception(state, dico)
    return cutDownAngle(state, dico['raySortie'], dico['rayInter'])

def passiveSituation(state, dico):
    """
    Quand le joueur n'a pas le controle sur
    la balle:
    - si la balle approche il s'approche pour
    recevoir la balle
    - s'il est le joueur le plus proche de la
    balle ou s'il vient de faire un dribble/controle
    il se dirige de nouveau vers la balle
    - si un coequipier a franchi une distance
    avec la balle, il monte de le terrain
    pour lui proposer des solutions
    - sinon il se decale lateralement
    """
    vectBall = (state.my_pos - state.ball_pos).normalize()
    vectSpeed = state.ball_speed.copy().normalize()
    if must_intercept(state, dico['rayRecept']) and vectSpeed.dot(vectBall) >= dico['angleRecept']:
        return tryInterception(state, dico)
    if state.is_nearest_ball() or \
    (had_ball_control(state, dico['rayReprise'], dico['angleReprise']) and state.is_nearest_ball_my_team()):
        return tryInterception(state, dico)
    if is_close_goal(state, dico['distAttaque']) and ball_advances(state) \
       and state.is_nearest_ball_my_team():
        return tryInterception(state, dico)
    if must_advance(state, dico['distMontee']):
        return pushUp(state, dico['coeffPushUp'])
    if state.is_nearest_ball_my_team() and must_intercept(state, dico['rayInter']):
        return tryInterception(state, dico)
    if state.numPlayers == 4:
        opp = free_opponent(state, dico['distDefZone'], dico['rayPressing'])
        if is_defensive_zone(state, dico['distDefZone']) and opp is not None:
            return mark(state, opp, dico['rayPressing'])
    if state.numPlayers == 2:
        opp = free_opponent(state, dico['distDefZone']+20., dico['rayPressing'])
        if opp is not None and not is_close_ball(state, opp.position):
            return mark(state, opp, dico['rayPressing'])
    if is_defensive_zone(state, dico['distDefZone']+20) and state.team_controls_ball():
        return loseMark(state, dico['rayPressing'], dico['distDemar'], dico['angleInter'])
    return cutDownAngle(state, dico['distShoot'], dico['rayInter'])

def loseMark(state, rayPressing, distDemar, angleInter):
    """
    Se demarque de l'adversaire le plus proche
    s'il en a un, se decale sinon
    """
    opp = state.nearest_opponent(rayPressing)
    if opp is None:
        return shiftAside(state, distDemar, angleInter)
    return shiftAsideMark(state, opp, distDemar)

def mark(state, opp, distMar):
    """
    Se positionne a une distance distMar
    de opp tout en lui bloquant la trajectoire
    de reception de la balle
    """
    vect = (state.ball_pos - opp.position).normalize()
    vect.norm = distMar
    return goTo(state, opp.position + vect)

def shiftAside(state, distDemar, angleInter):
    """
    Se decale lateralement pour avoir
    une meilleure reception de la balle
    """
    opp = state.nearest_opp
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
    Se decale en s'eloignant
    de l'adversaire
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

def goForwardsMFSolo(state, dico):
    """
    Essaye d'avance sur le milieu de terrain
    avec la balle et dribble lorsqu'il y a
    un adversaire en face
    """
    oppDef = nearest_defender(state, state.opponents, dico['rayDribble'])
    if oppDef is None:
        return control(state, dico['controleMT'])
    return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])

def goForwardsPASolo(state, dico):
    """
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

def goForwardsPA(state, dico):
    """
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
               must_assist(state, tm, dico['distPasse'], dico['angleInter'], dico['coeffPushUp']/2.):
                return passBall(state,tm,dico['powerPasse'],dico['thetaPasse'],dico['coeffPushUp']/2.)+\
                    pushUp(state, dico['coeffPushUp'])
            if must_pass_ball(state, tm, dico['distPasse'], dico['angleInter']):
                return passBall(state,tm,dico['powerPasse'],dico['thetaPasse'],dico['coeffPushUp'])+\
                    pushUp(state, dico['coeffPushUp'])
        return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])
    # if distance_horizontale(state.my_pos, state.opp_goal) < 30.:
    #     if tm is not None and must_assist(state, tm, distPasse, angleInter, coeffPushUp):
    #         return passBall(state, tm, powerPasse, thetaPasse, 0.)+pushUp(state, coeffPushUp)
    #     else:
    #         return goalControl(state, powerControl)
    return control(state, dico['controleAttaque'])

def goForwardsMF(state, dico):
    """
    Essaye d'avance sur le milieu de terrain
    avec la balle et dribble lorsqu'il y a
    un adversaire en face
    """
    oppDef = nearest_defender(state, state.opponents, dico['rayDribble'])
    if oppDef is not None:
        tm = free_teammate(state, dico['angleInter'])
        if tm is not None and must_pass_ball(state, tm, dico['distPasse'], dico['angleInter']):# and random.random() < 0.5:
            return passBall(state, tm, dico['powerPasse'], dico['thetaPasse'], dico['coeffPushUp'])+\
                pushUp(state, dico['coeffPushUp'])
        return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])
    return control(state, dico['controleMT'])

def goForwardsDef(state, dico):
    """
    Essaye d'avance sur la zone defensive
    avec la balle et dribble lorsqu'il y a
    un adversaire en face
    """
    angleInter = 5.*dico['angleInter']/4.
    #angleInter = dico['angleInter']
    oppDef = nearest_defender_def(state, state.opponents, dico['rayDribble'])
    if oppDef is not None:
        tm = free_teammate(state, angleInter)
        if tm is not None and must_pass_ball(state, tm, dico['distPasse'], angleInter) \
           and not is_under_pressure(state, tm, dico['rayPressing']):
            return passBall(state, tm, dico['powerPasse'], dico['thetaPasse'], dico['coeffPushUp'])+\
                pushUp(state, dico['coeffPushUp'])
        return clear_gk(state, angleClear=1.2)
    return control(state, dico['controleMT'])

def st_kickOff(state, dico):
    """
    """
    count = both_must_kick(state)
    if count > 1:
        return cutDownAngle_gk(state, 40.)
    if has_ball_control(state):
        if count == 1:
            return shoot(state, maxPlayerShoot)
        return control(state, dico['controleMT'])
    return goToBall(state)

def gk_kickOff(state, dico):
    """
    """
    count = both_must_kick(state)
    if count != 1:
        return cutDownAngle_gk(state, 40.)
    if has_ball_control(state):
        return kickAt(state, Vector2D(state.opp_goal.x, 100.), maxPlayerShoot)
    return goToBall(state)

def clearSolo(state):
    """
    Degage la balle avec une trajectoire
    horizontale a partir de sa position vers
    la cage adverse
    """
    profondeurDegagement = GAME_WIDTH/5.
    largeurDegagement = GAME_HEIGHT/4.
    vect = state.attacking_vector
    return kickAt(state, vect+state.ball_pos, 4.)
    ecart_x = profondeurDegagement
    if not state.is_team_left(): ecart_x = -ecart_x
    x = state.my_pos.x + ecart_x
    ecart_y = largeurDegagement
    if not is_upside(state.my_pos,state.nearest_opp.position):  ecart_y = -ecart_y
    y = state.my_pos.y + ecart_y
    return kickAt(state,Vector2D(x,y), maxPlayerShoot)

def clear_gk(state, angleClear=1., power=3.5):
    """
    Degage la balle dans sa ligne
    horizontale si personne ne le
    presse, fait une ouverture
    d'un certain angle par rapport
    a l'adversaire le marquant s'il
    y en a un
    """
    opp = state.nearest_opp
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

def pushUp(state, coeffPushUp):
    """
    Monte dans le terrain pour proposer
    des possibilites de passe aux
    coequipiers
    """
    if state.numPlayers == 4:
        return pushUp4v4(state, coeffPushUp)
    return pushUp2v2(state, coeffPushUp)

def pushUp4v4(state, coeffPushUp):
    """
    C.f. pushUp
    Specifique au 4v4
    TODO: Quid des nombres magiques ?
    Hypothese: CB c'est le joueur 1
    """
    porteur = nearest_state(state.ball_pos, state.teammates)
    tm_list = state.teammates[1::]
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
    TODO: Quid des nombres magiques ?
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
    Sort de la cage pour reduire
    l'angle de frappe a l'attaquant
    adverse
    """
    position = state.my_goal
    diff = state.ball_pos - position
    diff.norm = max(raySortie, diff.norm - rayInter)
    position += diff
    return goTo(state,position)

def cutDownAngle_gk(state, raySortie):
    """
    Sort de la cage pour reduire
    l'angle de frappe a l'attaquant
    adverse
    """
    position = state.my_goal
    diff = state.ball_pos - position
    diff.norm = raySortie
    position += diff
    return goTo(state,position)

def cutDownAngle_def(state, raySortie, rayInter):
    """
    Sort de la cage pour reduire
    l'angle de frappe a l'attaquant
    adverse
    """
    position = state.my_goal
    diff = state.ball_pos - position
    diff.norm = max(min(raySortie, diff.norm - rayInter), 20.)
    position += diff
    return goTo(state,position)

def tryInterception(state, dico):
    """
    Essaye d'intercepter la balle
    s'il lui reste de temps,
    reinitialise son compteur et
    rest immobile sinon
-    """
    if dico['n'] == -1:
        dico['n'] = dico['tempsI']
    dico['n'] -= 1
    if dico['n'] < 0 :
        dico['n'] = dico['tempsI']
        return goToBall(state)
    return interceptBall(state, dico['n']+1)

def interceptBall(state,n):
    """
    Se deplace en vue d'intercepter
    la balle pour une estimation
    de n instants de temps
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
