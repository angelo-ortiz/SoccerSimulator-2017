# -*- coding: utf-8 -*-
from .tools import Wrapper, StateFoot, is_in_radius_action, distance_horizontale, nearest_ball
from soccersimulator.settings import GAME_WIDTH, GAME_GOAL_HEIGHT, GAME_HEIGHT, BALL_RADIUS, \
        PLAYER_RADIUS

profondeurDegagement = GAME_WIDTH/5.
largeurDegagement = GAME_HEIGHT/4.
surfRep = GAME_HEIGHT/2.
distMaxInterception = GAME_WIDTH/6.
n_inst = [23.]*8 #[40.]*4
courte = [False]*8
distInterceptionCourte = GAME_GOAL_HEIGHT
interceptionCourte = 7. #15.
interceptionLongue = 23. #40.

def must_intercept(stateFoot, rayInter=distMaxInterception):
    """
    Renvoie vraie ssi le joueur est a une distance
    inferieure ou egale a distInter de la balle
    """
    if not is_in_radius_action(stateFoot, stateFoot.my_pos, rayInter):
        return False
    return stateFoot.is_nearest_ball()
    #return True

def is_under_pressure(stateFoot, joueur, rayPressing):
    """
    Renvoie vrai ssi il y a un adversaire a une
    distance inferieure ou egale a rayPressing
    """
    opp = nearest(stateFoot, joueur, stateFoot.opponents())
    return stateFoot.distance(opp) < rayPressing

def free_teammate(stateFoot, rayPressing):
    """
    Renvoie vrai ssi il y a un coequipier libre
    de marquage
    """
    tm = stateFoot.teammates()
    for p in tm:
        if not is_under_pressure(stateFoot, p, rayPressing):
            return p
    return None

def is_in_box(stateFoot, attaque=True):
    """
    Renvoie vrai ssi le joueur est dans sa
    surface de reparation si attaque est
    faux, celle adverse sinon
    """
    goal = stateFoot.my_goal
    if attaque: goal = stateFoot.opp_goal
    return is_in_radius_action(stateFoot, goal, surfRep)

def is_close_ball(stateFoot):
    """
    Renvoie vrai ssi le joueur est proche de la
    balle d'une telle maniere qu'il pourrait
    frapper
    """
    return stateFoot.distance(stateFoot.ball_pos) <= PLAYER_RADIUS + BALL_RADIUS

def is_close_goal(stateFoot, distance=27.):
    """
    TODO comparer a is_in_box
    """
    return is_in_radius_action(stateFoot, stateFoot.opp_goal, distance)

def must_advance(stateFoot, distMontee):
    """
    Renvoie vrai ssi le balle est loin de la
    cage et elle s'en eloigne
    """
    return stateFoot.distance_ball(stateFoot.my_goal) >= distMontee and \
            stateFoot.ball_speed.dot(stateFoot.ball_pos-stateFoot.my_goal) > 0

def must_defend_goal(stateFoot, distSortie):
    """
    Renvoie vrai ssi la balle est a une distance
    moyennement loin, i.e. le gardien doit sortir
    couvrir plus d'angle face a l'attaquant
    """
    return is_in_radius_action(stateFoot, stateFoot.my_pos, distSortie)

def must_intercept_gk(stateFoot, distance=20.):
    return is_in_radius_action(stateFoot, stateFoot.my_goal, distance)

def has_ball_control(stateFoot):
    """
    Renvoie vrai ssi le joueur a la balle au pied
    et le moteur du jeu lui permet de frapper
    """
    return is_close_ball(stateFoot) and stateFoot.player_state(*stateFoot.key).can_shoot()

def is_defense_zone(state, distDefZone=20.):#TODO distDefensZone variable
    """
    Renvoie vrai ssi la distance horizontale
    entre le joueur et sa cage est inferieure
    a distDefZone, i.e. il doit arreter de
    suivre l'adversaire et se demarquer
    """
    #return distance_horizontale(state.my_pos, state.my_goal) < (state.width/2.-profondeurDegagement)
    return distance_horizontale(state.my_pos, state.my_goal) < distDefZone

def high_precision_shoot(state, dist):
    """
    TODO quoi faire de cette fonction
    """
    return state.my_pos.distance(state.opp_goal) < dist

def temps_interception(state):
    """
    TODO quoi faire de cette fonction
    """
    idp = 4*(state.my_team-1) + state.me
    if not courte[idp] and is_in_radius_action(state, state.my_pos, distInterceptionCourte):
        courte[idp] = True
        n_inst[idp] = interceptionCourte
    if courte[idp] and not is_in_radius_action(state, state.my_pos, distInterceptionCourte):
        courte[idp] = False
        n_inst[idp] = interceptionLongue
    n_inst[idp] -= 1
    if n_inst[idp] == 0:
        n_inst[idp] = interceptionCourte if courte[idp] else interceptionLongue
    return n_inst[idp]

def empty_goal(strat, state, opp, angle):
    """
    TODO quoi faire de cette fonction
    """
    vGoal = (state.opp_goal - state.ball_pos).normalize()
    vOpp = (opp.position - state.ball_pos).normalize()
    if vGoal.dot(vOpp) <= angle:
        #print(vGoal.dot(vOpp))
        return True
    try:
        strat.dribbleGardien = not strat.dribbleGardien
    except AttributeError:
        strat.dribbleGardien = True
    return not strat.dribbleGardien
