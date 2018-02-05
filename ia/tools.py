# -*- coding: utf-8 -*-
from soccersimulator  import Strategy, SoccerAction, Vector2D
from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from soccersimulator.settings import *
from math import sqrt,ceil

accelerationShoot = 3.5
profondeurDegagement = GAME_WIDTH/4.8
distanceHorizontaleMaxInterception = GAME_WIDTH/6.
distanceMaxInterception = GAME_WIDTH/3.
distanceInterceptionCourte = GAME_WIDTH/15.
interceptionCourte = 3
interceptionLongue = 10
n_inst = [100.]*4
courte = [False]*4

#TODO
# my_pos, my_vitesse, ball_pos, ball_vitesse => property

## StateFoot ...
class StateFoot(object):
    def __init__(self,state,id_team,id_player):
        self.state = state
        self.key = (id_team,id_player)
    @property
    def id_team(self):
        return self.key[0]
    @property
    def id_team_adverse(self):
        return 3 - self.id_team
    def is_team_left(self):
        return self.id_team == 1
    @property
    def id_player(self):
        return self.key[1]
    def my_position(self):
        return self.state.player_state(*self.key).position
    def my_vitesse(self):
        return self.state.player_state(*self.key).vitesse
    def ball_position(self):
        return self.state.ball.position
    def ball_vitesse(self):
        return self.state.ball.vitesse
    def est_en_dessus(self,j):
        r = self.my_position()
        return r.y < j.position.y
    def doit_intercepter(self):
        ma_position = self.my_position()
        if abs(self.ma_cage.x-ma_position.x) > distanceHorizontaleMaxInterception or \
                self.distance_cage_joueur() > distanceMaxInterception:
                    return False
        return self.est_plus_proche(self.adversaires()) 
    @staticmethod
    def distance(p1,p2):
        return (p1-p2).norm 
    def distance_ball(self,p):
        return StateFoot.distance(self.ball_position(),p)
    def distance_ball_joueur(self):
        return self.distance_ball(self.my_position())
    def distance_cage_joueur(self):
        return StateFoot.distance(self.ma_cage,self.my_position())
    def est_plus_proche(self,liste_p):
        #dist_ball_p = self.distance_ball(p)
        #return self.distance_ball_joueur() < dist_ball_p
        for p in liste_p:
            if self.distance_ball_joueur() >= self.distance_ball(p.position):
                return False
        return True
    def adversaire_le_plus_proche(self):
        liste = self.adversaires()
        adv = liste[0]
        dist = self.distance_ball(adv.position)
        for p in liste[1:]:
            if self.distance_ball(p.position) < dist:
                adv = p
        return adv
    def adversaire_1v1(self):
        return self.state.player_state(self.id_team_adverse(),0)
    def adversaires(self):
        team = self.id_team_adverse
        return [self.state.player_state(team,i) for i in range(self.state.nb_players(team))]
    def can_shoot(self):
        dist_ball_joueur = self.distance_ball_joueur()
        ball_est_proche = dist_ball_joueur <= PLAYER_RADIUS + BALL_RADIUS
        return ball_est_proche and self.state.player_state(*self.key).can_shoot()
    @property
    def cage_adverse(self):
        return Vector2D(GAME_WIDTH if self.is_team_left() else 0.,GAME_HEIGHT/2.)
    @property
    def ma_cage(self):
        return Vector2D(0. if self.is_team_left() else GAME_WIDTH,GAME_HEIGHT/2.)

def normaliser_diff(src, dst, norme):
    return (dst-src).norm_max(norme)

def coeff_vitesse_reduite(n,fc):
    return (1.-fc)*(1.-(1.-fc)**n)/fc
