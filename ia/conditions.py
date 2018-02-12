# -*- coding: utf-8 -*-
from .tools import *

distMaxFonceurCh1Shoot = GAME_WIDTH/3.
distMaxFonceurNormShoot = GAME_WIDTH/4.
distMaxInterception = GAME_WIDTH/3.
distHorizontaleMaxInterception = GAME_WIDTH/6.
distInterceptionCourte = GAME_WIDTH/15.

def doit_intercepter(stateFoot):
    if distance_horizontale(stateFoot.cage, stateFoot.position) > distHorizontaleMaxInterception or \
            stateFoot.distance_cage_joueur() > distMaxInterception:
                return False
    return stateFoot.est_plus_proche() 
def can_shoot(stateFoot):
    dist_ball_joueur = stateFoot.distance_ball_joueur()
    ball_est_proche = dist_ball_joueur <= PLAYER_RADIUS + BALL_RADIUS
    return ball_est_proche and stateFoot.state.player_state(*stateFoot.key).can_shoot()

def high_precision_shoot(state):
    return distance(state.cage_adverse,state.position) < distMaxFonceurNormShoot

def high_precision_shoot_ch1(state):
    return distance(state.cage_adverse,state.position) < distMaxFonceurCh1Shoot

def temps_interception(state):
    if state.distance_ball_joueur() < distInterceptionCourte:
        return interceptionCourte
    return interceptionLongue
