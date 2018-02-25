# -*- coding: utf-8 -*-
from .tools import Wrapper, StateFoot, is_in_radius_action, distance_horizontale 
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

def must_intercept(stateFoot):
    if not is_in_radius_action(stateFoot, stateFoot.position, distMaxInterception):
        return False
    return stateFoot.is_nearest_ball() 

def is_in_box(stateFoot, attaque=True):
    goal = stateFoot.my_goal
    if attaque: goal = stateFoot.opp_goal
    return is_in_radius_action(stateFoot, goal, surfRep) 

def is_close_ball(stateFoot):
    return stateFoot.distance(stateFoot.ball_pos) <= PLAYER_RADIUS + BALL_RADIUS

def is_close_goal(stateFoot):
    return is_in_radius_action(stateFoot, stateFoot.opp_goal, 27.)

def must_intercept_gk(stateFoot, distance=20.):
    return is_in_radius_action(stateFoot, stateFoot.my_goal, distance) 

def can_shoot(stateFoot):
    return is_close_ball(stateFoot) and stateFoot.player_state(*stateFoot.key).can_shoot()

def is_defense_zone(state):
    return distance_horizontale(state.my_pos, state.my_goal) < (state.width/2.-profondeurDegagement)

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
