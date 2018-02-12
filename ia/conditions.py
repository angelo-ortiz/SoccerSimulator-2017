# -*- coding: utf-8 -*-
from .tools import *

distMaxFonceurCh1Shoot = GAME_WIDTH/3.
distMaxFonceurNormShoot = GAME_WIDTH/4.
distMaxInterceptionGoal = GAME_HEIGHT/2.
distMaxInterception = GAME_WIDTH/6.
n_inst = [100.]*4 # vrai_temps + 1
courte = [False]*4
distInterceptionCourte = GAME_GOAL_HEIGHT
interceptionCourte = 3 # vrai_temps + 1
interceptionLongue = 10

def doit_intercepter(stateFoot):
    #TODO a modifier : pour l'instant, pas utilisee
    if not est_dans_zone(stateFoot, stateFoot.position, distMaxInterception):
        return False
    return stateFoot.est_plus_proche() 

def doit_intercepter_goal(stateFoot):
    return est_dans_zone(stateFoot, stateFoot.cage, distMaxInterceptionGoal)

def can_shoot(stateFoot):
    dist_ball_joueur = stateFoot.distance_ball_joueur()
    ball_est_proche = dist_ball_joueur <= PLAYER_RADIUS + BALL_RADIUS
    return ball_est_proche and stateFoot.state.player_state(*stateFoot.key).can_shoot()

def high_precision_shoot(state, dist):
    return distance(state.cage_adverse,state.position) < dist

def temps_interception(state):
    idp = state.id_player
    if not courte[idp] and est_dans_zone(state, state.position, distInterceptionCourte):
        courte[idp] = True
        n_inst[idp] = interceptionCourte
    n_inst[idp] -= 1
    return n_inst[idp]
