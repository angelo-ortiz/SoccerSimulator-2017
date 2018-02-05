# -*- coding: utf-8 -*-
from soccersimulator  import Strategy, SoccerAction, Vector2D
from soccersimulator import SoccerTeam, Simulation
from soccersimulator import show_simu
from soccersimulator.settings import *

accelerationShoot = 3.5
profondeurDegagement = GAME_WIDTH/4.8
distanceHorizontaleMaxInterception = GAME_WIDTH/6.
distanceMaxInterception = GAME_WIDTH/3.
interceptionCourte = 3.
interceptionLongue = 10.
distanceInterceptionCourte = GAME_WIDTH/15.

## StateFoot ...
class StateFoot(object):
    def __init__(self,state,id_team,id_player):
        self.state = state
        self.key = (id_team,id_player)
    def id_team(self):
        return self.key[0]
    def id_team_adverse(self):
        return 3 - self.id_team()
    def is_team_left(self):
        return self.id_team() == 1
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
    def coeff_vitesse_reduite(self,n,fc):
        return (1-(1-fc)**(n+1))/fc
    def go_to_ball(self,n):
        # n = 10
        v = self.my_vitesse()
        r = self.my_position()
        vb = self.ball_vitesse()
        rb = self.ball_position()
        #ax = (10*(v.x-vb.x)+r.x-rb.x)/(-50)
        #ay = (10*(v.y-vb.y)+r.y-rb.y)/(-50)
        #ax = 2.*(n*v.x-vb.x*self.coeff_vitesse_reduite(n,ballBrakeConstant)+r.x-rb.x)/(n*n)
        #ay = 2.*(n*v.y-vb.y*self.coeff_vitesse_reduite(n,ballBrakeConstant)+r.y-rb.y)/(n*n)
        ax = -ballBrakeConstant*((v.x-vb.x)*self.coeff_vitesse_reduite(n,ballBrakeConstant)+r.x-rb.x)/(n-(1-ballBrakeConstant)*self.coeff_vitesse_reduite(n-1,ballBrakeConstant))
        ay = -ballBrakeConstant*((v.y-vb.y)*self.coeff_vitesse_reduite(n,ballBrakeConstant)+r.y-rb.y)/(n-(1-ballBrakeConstant)*self.coeff_vitesse_reduite(n-1,ballBrakeConstant))
        return self.aller_acc(Vector2D(ax,ay))
    def aller_acc(self,p):
        return SoccerAction(p)
    def aller_dest(self,p):
        return self.aller_acc(p-self.my_position())
    def shoot(self,p,degager=False):
        puissance = accelerationShoot if not degager else maxPlayerShoot
        return SoccerAction(Vector2D(),(p-self.ball_position()).norm_max(puissance))
    def est_en_dessus(self,j):
        r = self.my_position()
        return r.y < j.position.y
    def degager(self):
        ecart_x = profondeurDegagement
        if not self.is_team_left() : ecart_x = -ecart_x 
        x = self.my_position().x + ecart_x
        v = self.my_vitesse()
        y = 0. if self.est_en_dessus(self.adversaire_le_plus_proche()) else GAME_HEIGHT
        #y = 0. if v.y < 0. else GAME_HEIGHT
        return self.shoot(Vector2D(x,y))
    def doit_intercepter(self):
        ma_cage = self.ma_cage()
        ma_position = self.my_position()
        if abs(ma_cage.x-ma_position.x) > distanceHorizontaleMaxInterception or \
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
        return StateFoot.distance(self.ma_cage(),self.my_position())
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
        team = self.id_team_adverse()
        return [self.state.player_state(team,i) for i in range(self.state.nb_players(team))]
    def can_shoot(self):
        dist_ball_joueur = self.distance_ball_joueur()
        ball_est_proche = dist_ball_joueur <= PLAYER_RADIUS + BALL_RADIUS
        return ball_est_proche and self.state.player_state(*self.key).can_shoot()
    def cage_but(self):
        return Vector2D(GAME_WIDTH if self.is_team_left() else 0.,GAME_HEIGHT/2.)
    def ma_cage(self):
        return Vector2D(0. if self.is_team_left() else GAME_WIDTH,GAME_HEIGHT/2.)
    def compute_strategy(self):
        #TODO
        return self.aller(Vector2D())
