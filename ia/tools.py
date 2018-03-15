# -*- coding: utf-8 -*-
from soccersimulator  import SoccerAction, Vector2D
from soccersimulator.settings import GAME_HEIGHT, GAME_WIDTH, GAME_GOAL_HEIGHT

## Classe enveloppe de notre super-etat du jeu
class Wrapper(object):
    def __init__(self,state):
        self._obj = state
    def __getattr__(self,attr):
        return getattr(self._obj,attr)


## StateFoot
#### C'est notre super-etat du jeu
#### Il nous facilite l'acces a certains aspects
#### de la configuration courante du terrain
#### depuis la perspective d'un joueur
class StateFoot(Wrapper):
    def __init__(self,state,id_team,id_player):
        super(StateFoot,self).__init__(state)
        self.key = (id_team,id_player)

    @property
    def my_team(self):
        """
        Son equipe
        """
        return self.key[0]

    @property
    def opp_team(self):
        """
        L'equipe adverse
        """
        return 3 - self.my_team

    @property
    def me(self):
        """
        Son identifiant
        """
        return self.key[1]

    @property
    def my_pos(self):
        """
        Sa position courante
        """
        return self.player_state(*self.key).position

    @property
    def my_speed(self):
        """
        Sa vitesse courante
        """
        return self.player_state(*self.key).vitesse

    @property
    def ball_pos(self):
        """
        La position courante de la balle
        """
        return self.ball.position

    @property
    def ball_speed(self):
        """
        La vitesse courante de la balle
        """
        return self.ball.vitesse

    @property
    def my_goal(self):
        """
        La position du centre de sa cage
        """
        return Vector2D((self.my_team - 1) * self.width,self.goal_height)

    @property
    def opp_goal(self):
        """
        La position du centre de la cage adverse
        """
        return Vector2D((self.opp_team - 1) * self.width,self.goal_height)

    @property
    def height(self):
        """
        La hauteur du terrain
        """
        return GAME_HEIGHT

    @property
    def width(self):
        """
        La largeur du terrain
        """
        return GAME_WIDTH

    @property
    def goal_height(self):
        """
        La hauteur du point central
        """
        return self.height/2.

    @property
    def center_point(self):
        """
        La position du point central
        """
        return Vector2D(self.width/2., self.goal_height)

    def teammates(self):
        """
        Ses coequipiers
        """
        team = self.my_team
        liste = [self.player_state(team,i) for i in range(self.nb_players(team))]
        liste.remove(self.player_state(*self.key))
        return liste

    def opponents(self):
        """
        Ses adversaires
        """
        team = self.opp_team
        return [self.player_state(team,i) for i in range(self.nb_players(team))]

    @property
    def nearest_opp(self):
        """
        L'adversaire le plus proche de la balle
        """
        liste = self.opponents()
        opp = liste[0]
        dist = self.distance_ball(opp.position)
        for p in liste[1:]:
            if self.distance_ball(p.position) < dist:
                opp = p
        return opp

    def opponent_1v1(self):
        """
        Son adversaire lorsque c'est un match 1v1
        """
        return self.player_state(self.opp_team,0)

    def quadrant(self):
        """
        Renvoie le quadrant trigonometrique dans lequel
        se trouve le joueur
        """
        mp = self.my_pos
        cp = self.center_point
        if mp.x < cp.x:
            if mp.y > cp.y:
                return "II"
            else:
                return "III"
        else:
            if mp.y > cp.y:
                return "I"
            else:
                return "IV"

    def is_team_left(self):
        """
        Renvoie vrai ssi son equipe joue a gauche
        """
        return self.my_team == 1

    def distance_ball(self,ref):
        """
        Renvoie la distance entre la balle et un point
        de reference
        """
        return ref.distance(self.ball_pos)

    def distance(self,ref):
        """
        Renvoie la distance entre le joueur et un point
        de reference
        """
        return ref.distance(self.my_pos)

    def is_nearest_ball(self):
        """
        Renvoie vrai ssi il est le joueur le plus proche
        de la balle
        """
        liste_opp = self.opponents()
        dist_ball_joueur = self.distance(self.ball_pos)
        for opp in liste_opp:
            if dist_ball_joueur >= self.distance_ball(opp.position):
                return False
        return True



def normalise_diff(src, dst, norme):
    """
    Renvoie le vecteur allant de src vers dst avec
    comme norme maximale norme
    """
    return (dst-src).norm_max(norme)

def coeff_vitesse_reduite(n,fc):
    """
    Renvoie le coefficient de la vitesse dans le calcul
    de l'acceleration pour l'interception compte tenu
    des effets de frottement
    """
    return (1.-fc)*(1.-(1.-fc)**n)/fc

def is_in_radius_action(stateFoot,ref,distLimite):
    """
    Renvoie vrai ssi le point de reference se trouve
    dans le cercle de rayon distLimite centre en la
    position de la balle
    """
    return ref.distance(stateFoot.ball_pos) <= distLimite

def distance_horizontale(v1, v2):
    """
    Renvoie la distance entre les abscisses de deux
    points
    """
    return abs(v1.x-v2.x)

def is_upside(ref,other):
    """
    Renvoie vrai ssi la reference est au-dessus de
    l'autre point
    """
    return ref.y > other.y

def get_random_vector():
    """
    Renvoie un vecteur a coordonnees aleatoires comprises
    entre -1 et 1 (exclu)
    """
    return Vector2D.create_random(-1.,1.)

def get_random_strategy():
    """
    Renvoie une SoccerAction completement aleatoire, i.e.
    les vecteurs de frappe et acceleration le sont
    """
    return SoccerAction(get_random_vector(), get_random_vector())

def get_empty_strategy():
    """
    Renvoie une SoccerAction qui ne fait rien du tout
    """
    return SoccerAction()

def nearest(ref, liste):
    """
    Renvoie la position du joueur le plus proche de la
    reference parmi une liste passee en parametre
    """
    p = None
    distMin = 1024.
    for o in liste:
        dist = ref.distance(o.position)
        if dist < distMin:
            p = o
            distMin = dist
    return p.position

def nearest_ball(stateFoot, liste):
    """
    Renvoie la position du joueur le plus proche de la balle
    """
    return nearest(stateFoot.ball_pos, liste)

def free_continue(stateFoot, liste, distRef):
    """
    Renvoie vrai si le joueur n'a pas d'opposition dans un
    rayon de distRef en direction de la cage opposee, i.e. il
    a une voie libre pour continuer, sinon l'adversaire le
    plus proche qui est susceptible de l'intercepter
    """
    j = None
    og = stateFoot.opp_goal
    dog = stateFoot.distance(og)
    dist_min = distRef
    for i in liste:
        dist_i = stateFoot.distance_ball(i.position)
        if dist_i < dist_min and dog > i.position.distance(og):
            j = i
            dist_min = dist_i
    if j is not None:
        return j
    return True

