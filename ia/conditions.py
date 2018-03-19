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
    if not is_in_radius_action(stateFoot, stateFoot.my_pos, rayInter):
        return False
    #return stateFoot.is_nearest_ball() #TODO ceci a remettre 
    return True

def is_under_pressure(stateFoot, joueur, rayPressing):
    opp = nearest(stateFoot, joueur, stateFoot.opponents())
    return stateFoot.distance(opp) < rayPressing

def free_teammate(stateFoot, rayPressing):
    tm = stateFoot.teammates()
    for p in tm:
        if not is_under_pressure(stateFoot, p, rayPressing):
            return p
    return None

def is_in_box(stateFoot, attaque=True):
    goal = stateFoot.my_goal
    if attaque: goal = stateFoot.opp_goal
    return is_in_radius_action(stateFoot, goal, surfRep) 

def is_close_ball(stateFoot):
    return stateFoot.distance(stateFoot.ball_pos) <= PLAYER_RADIUS + BALL_RADIUS

def is_close_goal(stateFoot, distance=27.):
    return is_in_radius_action(stateFoot, stateFoot.opp_goal, distance)

def must_advance(stateFoot, distMontee):
    return stateFoot.distance_ball(stateFoot.my_goal) >= distMontee and \
            stateFoot.ball_speed.dot(stateFoot.ball_pos-stateFoot.my_goal) > 0

def must_defend_goal(stateFoot, distSortie):
    return is_in_radius_action(stateFoot, stateFoot.my_pos, distSortie)

def must_intercept_gk(stateFoot, distance=20.):
    return is_in_radius_action(stateFoot, stateFoot.my_goal, distance) 

def has_ball_control(stateFoot):
    return is_close_ball(stateFoot) and stateFoot.player_state(*stateFoot.key).can_shoot()

def is_defense_zone(state, distDefZone=20.):#TODO distDefensZone variable
    #return distance_horizontale(state.my_pos, state.my_goal) < (state.width/2.-profondeurDegagement)
    return distance_horizontale(state.my_pos, state.my_goal) < distDefZone

def high_precision_shoot(state, dist):
    return state.my_pos.distance(state.opp_goal) < dist

def temps_interception(state):
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
