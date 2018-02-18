# -*- coding: utf-8 -*-
from soccersimulator  import Strategy, SoccerAction, Vector2D
from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from soccersimulator.settings import *

profondeurDegagement = GAME_WIDTH/4.8
longueurSurfaceReparation = GAME_WIDTH/6.

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
    @property
    def id_player(self):
        return self.key[1]
    @property
    def position(self):
        return self.state.player_state(*self.key).position
    @property
    def vitesse(self):
        return self.state.player_state(*self.key).vitesse
    @property
    def ball_position(self):
        return self.state.ball.position
    @property
    def ball_vitesse(self):
        return self.state.ball.vitesse
    @property
    def cage(self):
        return Vector2D(0. if self.is_team_left() else GAME_WIDTH,GAME_HEIGHT/2.)
    @property
    def cage_adverse(self):
        return Vector2D(GAME_WIDTH if self.is_team_left() else 0.,GAME_HEIGHT/2.)
    def is_team_left(self):
        return self.id_team == 1
    def est_en_dessus(self,j):
        return self.position.y < j.position.y
    def distance_ball(self,p):
        return distance(self.ball_position,p)
    def distance_ball_joueur(self):
        return self.distance_ball(self.position)
    def distance_cage_joueur(self):
        return distance(self.cage,self.position)
    def est_plus_proche(self):
        liste_adv = self.adversaires()
        dist_ball_joueur = self.distance_ball_joueur()
        for adv in liste_adv:
            if dist_ball_joueur >= self.distance_ball(adv.position):
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
    def is_in_goal_box(self):
        return distance_horizontale(ma_position, cage_adverse) <= longueurSurfaceReparation

def normaliser_diff(src, dst, norme):
    return (dst-src).norm_max(norme)

def coeff_vitesse_reduite(n,fc):
    return (1.-fc)*(1.-(1.-fc)**n)/fc

def distance(v1,v2):
    return (v1-v2).norm

def est_dans_zone(state,ref,distLimite):
    return distance(state.ball_position, ref) <= distLimite

def distance_horizontale(v1, v2):
    return abs(v1.x-v2.x)
