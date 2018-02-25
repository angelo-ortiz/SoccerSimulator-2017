# -*- coding: utf-8 -*-
from soccersimulator  import SoccerAction, Vector2D
from soccersimulator.settings import GAME_HEIGHT, GAME_WIDTH, GAME_GOAL_HEIGHT

class Wrapper(object):
    def __init__(self,state):
        self._obj = state
    def __getattr__(self,attr):
        return getattr(self._obj,attr)


## StateFoot ...
class StateFoot(Wrapper):
    def __init__(self,state,id_team,id_player):
        super(StateFoot,self).__init__(state)
        self.key = (id_team,id_player)
    
    @property
    def my_team(self):
        return self.key[0]
    
    @property
    def opp_team(self):
        return 3 - self.my_team
    
    @property
    def me(self):
        return self.key[1]
    
    @property
    def my_pos(self):
        return self.player_state(*self.key).position
    
    @property
    def my_speed(self):
        return self.player_state(*self.key).vitesse
    
    @property
    def ball_pos(self):
        return self.ball.position
    
    @property
    def ball_speed(self):
        return self.ball.vitesse
    
    @property
    def my_goal(self):
        return Vector2D((self.my_team - 1) * self.width,self.goal_height)
    
    @property
    def opp_goal(self):
        return Vector2D((self.opp_team - 1) * self.width,self.goal_height)
   
    @property
    def height(self):
        return GAME_HEIGHT

    @property
    def width(self):
        return GAME_WIDTH
    
    @property
    def goal_height(self):
        return self.height/2.

    @property
    def center_point(self):
        return Vector2D(self.width/2., self.goal_height)

    @property
    def nearest_opp(self):
        liste = self.opponents()
        opp = liste[0]
        dist = self.distance_ball(opp.position)
        for p in liste[1:]:
            if self.distance_ball(p.position) < dist:
                opp = p
        return opp

    def tt(self):
        team = self.my_team
        liste = []
        for i in range(self.nb_players(team)):
            if i != self.me:
                liste.append(self.player_state(team,i))
        #return [self.player_state(team,i) for i in range(self.nb_players(team))]
        return liste

    def is_team_left(self):
        return self.my_team == 1
    
    def distance_ball(self,ref):
        return ref.distance(self.ball_pos)
    
    def distance(self,ref):
        return ref.distance(self.my_pos)
    
    def is_nearest_ball(self):
        liste_opp = self.opponents()
        dist_ball_joueur = self.distance(self.ball_pos)
        for opp in liste_opp:
            if dist_ball_joueur >= self.distance_ball(opp.position):
                return False
        return True
    
    def opponent_1v1(self):
        return self.player_state(self.opp_team,0)
    
    def opponents(self):
        team = self.opp_team
        return [self.player_state(team,i) for i in range(self.nb_players(team))]
    

def normalise_diff(src, dst, norme):
    return (dst-src).norm_max(norme)

def coeff_vitesse_reduite(n,fc):
    return (1.-fc)*(1.-(1.-fc)**n)/fc

def is_in_radius_action(state,ref,distLimite):
    return ref.distance(state.ball_pos) <= distLimite

def distance_horizontale(v1, v2):
    return abs(v1.x-v2.x)
    
def is_upside(state,vect):
    return state.my_pos.y > vect.y
    
def get_random_vector():
    return Vector2D.create_random(-1.,1.)

def get_random_strategy():
    return SoccerAction(get_random_vector(), get_random_vector())

def get_empty_strategy():
    return SoccerAction()
