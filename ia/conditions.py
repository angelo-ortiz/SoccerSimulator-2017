# -*- coding: utf-8 -*-
from .tools import Wrapper, StateFoot, is_in_radius_action, distance_horizontale, \
    nearest, nearest_state, nearest_ball
from soccersimulator.settings import GAME_WIDTH, GAME_GOAL_HEIGHT, GAME_HEIGHT, BALL_RADIUS, \
        PLAYER_RADIUS
import random

def is_close_ball(stateFoot, player):
    """
    Renvoie vrai ssi le joueur est proche de la
    balle d'une telle maniere qu'il pourrait
    frapper
    """
    return is_in_radius_action(stateFoot, player, PLAYER_RADIUS + BALL_RADIUS)

def is_close_goal(stateFoot, distGoal=27.):
    """
    Renvoie vrai ssi le joueur est a une
    distance inferieure a distGoal de la
    cage adverse
    """
    return is_in_radius_action(stateFoot, stateFoot.opp_goal, distGoal) or \
        distance_horizontale(stateFoot.opp_goal, stateFoot.ball_pos) < distGoal-10.#5.

def is_kick_off(stateFoot):
    """
    Renvoie vrai ssi la balle est dans le
    centre du terrain
    """
    return stateFoot.center_spot == stateFoot.ball_pos
    #return stateFoot.distance_ball(stateFoot.center_spot) < 10.

def has_ball_control(stateFoot):
    """
    Renvoie vrai ssi le joueur a la balle au pied
    et le moteur du jeu lui permet de frapper
    """
    return is_close_ball(stateFoot, stateFoot.my_pos) and stateFoot.player_state(*stateFoot.key).can_shoot()

def had_ball_control(stateFoot, rayReprise, angleReprise):
    """
    Renvoie vrai ssi le joueur a eu la balle au pied
    juste avant cet instant, i.e. il a fait un
    controle ou un dribble
    """
    vectBall = (stateFoot.my_pos - stateFoot.ball_pos).normalize()
    vectSpeed = stateFoot.ball_speed.copy().normalize()
    return stateFoot.distance_ball(stateFoot.my_pos) < rayReprise and \
        vectSpeed.dot(vectBall) <= angleReprise

def must_intercept(stateFoot, rayInter=GAME_WIDTH/6.):
    """
    Renvoie vraie ssi le joueur est a une distance
    inferieure ou egale a distInter de la balle et
    en est le joueur le plus proche
    """
    if not is_in_radius_action(stateFoot, stateFoot.my_pos, rayInter):
        return False
    return stateFoot.is_nearest_ball()

def ball_advances(stateFoot):
    """
    Renvoie vrai ssi la balle se deplace en
    direction de la cage adverse
    """
    return stateFoot.ball_speed.dot(stateFoot.attacking_vector) >= 0.

def must_advance(stateFoot, distMontee):
    """
    Renvoie vrai ssi le balle est loin de la
    cage et elle s'en eloigne
    """
    control = stateFoot.team_controls_ball()
    if control is not None:
        return control
    if not ball_advances(stateFoot):
        return False
    ball_speed = stateFoot.ball_speed.copy().normalize()
    meBall = (stateFoot.ball_pos - stateFoot.my_pos).normalize()
    if meBall.dot(ball_speed) >= 0.995: return True
    for tm in stateFoot.teammates:
        tmBall = (stateFoot.ball_pos - tm.position).normalize()
        if tmBall.dot(ball_speed) >= 0.8: return True
    return False

def opponent_approaches_my_goal(stateFoot, distSortie):
    """
    Renvoie vrai ssi la balle est a une distance
    moyennement loin, i.e. le gardien doit sortir
    couvrir plus d'angle face a l'attaquant
    """
    return is_in_radius_action(stateFoot, stateFoot.my_goal, distSortie)

def is_under_pressure(stateFoot, joueur, rayPressing):
    """
    Renvoie vrai ssi il y a un adversaire a une
    distance inferieure ou egale a rayPressing
    """
    opp = nearest(joueur.position, stateFoot.opponents)
    return joueur.position.distance(opp) < rayPressing

def is_defensive_zone(stateFoot, distDefZone=20.):
    """
    Renvoie vrai ssi la distance horizontale
    entre le joueur et sa cage est inferieure
    a distDefZone, i.e. il doit arreter de
    suivre l'adversaire et se demarquer
    """
    return stateFoot.distance(stateFoot.my_goal) < distDefZone \
        or distance_horizontale(stateFoot.my_pos, stateFoot.my_goal) < distDefZone-10.

def empty_goal(strat, stateFoot, opp, angle):
    """
    Renvoie vrai ssi il n'y a pas d'opposition
    dans un rayon angulaire d'angle vers la
    cage adverse ou si le joueur a deja
    dribble le gardien et il frappe directement
    """
    vGoal = (stateFoot.opp_goal - stateFoot.ball_pos).normalize()
    vOpp = (opp.position - stateFoot.ball_pos).normalize()
    if vGoal.dot(vOpp) <= angle:
        return True
    try:
        strat.dribbleGardien = not strat.dribbleGardien
    except AttributeError:
        strat.dribbleGardien = True
    return not strat.dribbleGardien

def free_teammate(stateFoot, angleInter):
    """
    Renvoie le premier coequipier libre de
    marquage
    """
    tm_best = None
    dist_best = 0.
    if stateFoot.numPlayers == 4:
        tmL = stateFoot.offensive_teammates
    else:
        tmL = stateFoot.teammates
    for tm in tmL:
        if stateFoot.free_pass_trajectory(tm, angleInter):
            opp = nearest(tm.position, stateFoot.opponents)
            dist = tm.position.distance(opp)
            # dist = stateFoot.distance(tm.position)
            if dist > dist_best:
                tm_best = tm
                dist_best = dist
    return tm_best


def free_opponent(stateFoot, distDefZone, rayPressing):
    """
    Renvoie l'adversaire dans la defensive de
    son equipe le plus proche de sa cage et sans
    marquage
    """
    oppAtt = None
    my_team = stateFoot.teammates + [stateFoot.my_state]
    if stateFoot.numPlayers == 4:
        my_team = my_team[2::]
    for opp in stateFoot.opponents:
        if distance_horizontale(stateFoot.my_goal, opp.position) > distDefZone:
            continue
        tm = nearest_state(opp.position, my_team)
        if stateFoot.distance_ball(opp.position) > rayPressing and tm.position == stateFoot.my_pos:
            oppAtt = opp
            break;
    return oppAtt

def must_defend(stateFoot):
    """
    Renvoie vrai ssi toute l'equipe est dans
    le camp adverse, l'equipe adverse controle
    la balle et lui, c'est le joueur le plus
    proche de sa cage
    """
    opp = stateFoot.nearest_opp
    pass
    return None

def must_pass_ball(stateFoot, tm, distPasse, angleInter):
    """
    Renvoie vrai ssi le coequipier du joueur est
    a une distance inferieure ou egale a distTM
    avec une probabilite de probPasse
    """
    #modif 20.
    if distance_horizontale(stateFoot.my_pos, stateFoot.opp_goal)+20.< \
       distance_horizontale(tm.position, stateFoot.opp_goal):
        return False
    return stateFoot.free_pass_trajectory(tm, angleInter)

def must_assist(stateFoot, tm, distPasse, angleInter, coeffPushUp):
    """
    Renvoie vrai si le jouer est dans une position
    trop decale de l'axe et qu'un coequipier est
    dans une meilleure position et la passe est
    tout a fait possible
    """
    if not must_pass_ball(stateFoot, tm, distPasse, angleInter):
        return False
    meVect = (stateFoot.my_pos - stateFoot.opp_goal).normalize()
    tmVect = (tm.position + coeffPushUp*tm.vitesse- stateFoot.opp_goal).normalize()
    ref = (stateFoot.my_goal - stateFoot.opp_goal).normalize()
    return ref.dot(meVect) < 0.7 and ref.dot(tmVect) >= 0.7

def both_must_kick(stateFoot):
    """
    """
    state = 0
    for opp in stateFoot.opponents:
        if stateFoot.distance_ball(opp.position) < 25.:
            state += 1
    return state
