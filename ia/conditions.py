# -*- coding: utf-8 -*-
from .tools import Wrapper, StateFoot, is_in_radius_action 
from soccersimulator.settings import GAME_WIDTH, GAME_GOAL_HEIGHT, GAME_HEIGHT, BALL_RADIUS, \
        PLAYER_RADIUS

surfRep = GAME_HEIGHT/2.
distMaxInterception = GAME_WIDTH/6.
n_inst = [10.]*4 #[40.]*4
courte = [False]*4
distInterceptionCourte = GAME_GOAL_HEIGHT
interceptionCourte = 5 #15.
interceptionLongue = 10 #40.

def must_intercept(stateFoot):
    if not is_in_radius_action(stateFoot, stateFoot.position, distMaxInterception):
        return False
    return stateFoot.is_nearest_ball() 

def is_in_box(stateFoot, attaque=True):
    goal = stateFoot.my_goal
    if attaque: goal = stateFoot.opp_goal
    return is_in_radius_action(stateFoot, goal, surfRep) 

def must_intercept_gk(stateFoot, distance):
    return is_in_radius_action(stateFoot, stateFoot.my_goal, distance) and stateFoot.is_nearest_ball() 

def can_shoot(stateFoot):
    dist_ball_joueur = stateFoot.distance(stateFoot.ball_pos)
    ball_est_proche = dist_ball_joueur <= PLAYER_RADIUS + BALL_RADIUS
    return ball_est_proche and stateFoot.player_state(*stateFoot.key).can_shoot()

def high_precision_shoot(state, dist):
    return state.my_pos.distance(state.opp_goal) < dist

def temps_interception(state):
    idp = state.me
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
