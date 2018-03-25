# -*- coding: utf-8 -*-
from soccersimulator  import SoccerAction, Vector2D
from soccersimulator.settings import GAME_HEIGHT, GAME_WIDTH, GAME_GOAL_HEIGHT, maxPlayerShoot
from math import acos, exp, asin, sin

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
    def my_state(self):
        """
        Son etat
        """
        return self.player_state(*self.key)

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
    def center_spot(self):
        """
        La position du point central
        """
        return Vector2D(self.width/2., self.goal_height)

    @property
    def quadrant(self):
        """
        Renvoie le quadrant trigonometrique dans lequel
        se trouve le joueur
        """
        mp = self.my_pos
        cp = self.center_spot
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

    @property
    def teammates(self):
        """
        Ses coequipiers
        """
        team = self.my_team
        liste = [self.player_state(team,i) for i in range(self.nb_players(team))]
        liste.remove(self.player_state(*self.key))
        return liste

    @property
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
        liste = self.opponents
        opp = liste[0]
        dist = self.distance_ball(opp.position)
        for p in liste[1:]:
            if self.distance_ball(p.position) < dist:
                opp = p
        return opp

    def nearest_opponent(self, rayPressing):
        """
        L'adversaire le plus proche du joueur
        """
        liste = self.opponents
        distMin = rayPressing
        opp = None
        for p in liste:
            dist = self.distance(p.position)
            if self.distance(p.position) < distMin:
                distMin = dist
                opp = p
        return opp

    def opponent_1v1(self):
        """
        Son adversaire lorsque c'est un match 1v1
        """
        return self.player_state(self.opp_team,0)

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
        liste_opp = self.opponents + self.teammates
        dist_ball_joueur = self.distance(self.ball_pos)
        for opp in liste_opp:
            if dist_ball_joueur >= self.distance_ball(opp.position):
                return False
        return True

    def is_nearest_ball_my_team(self):
        """
        Renvoie vrai ssi il est le joueur le plus proche
        de la balle
        """
        liste_opp = self.teammates
        dist_ball_joueur = self.distance(self.ball_pos)
        for opp in liste_opp:
            if dist_ball_joueur >= self.distance_ball(opp.position):
                return False
        return True

    def is_valid_position(self, pos):
        """
        Renvoie vrai ssi la position rentre dans le
        terrain de football
        """
        return pos.x >= 0. and pos.x < self.width \
            and pos.y >= 0. and pos.y < self.height

    def team_controls_ball(self):
        """
        """
        liste = [self.my_state] + self.teammates + self.opponents
        p = None
        distMin = 20.
        for o in liste:
            dist = self.distance_ball(o.position)
            if dist < distMin:
                p = o
                distMin = dist
        if p is not None:
            return not p in self.opponents
        return None

    def free_pass_trajectory(self, angleInter):
        """
        """
        tm = self.teammates[0]
        vect = (tm.position - self.my_pos).normalize()
        for opp in self.opponents:
            diff = opp.position-self.my_pos
            angle = get_oriented_angle(vect, diff.normalize())
            if self.is_team_left(): angle = -angle
            if angle >= 0. and angle < angleInter:
                return False
        return True


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

def normalise_diff(src, dst, norme):
    """
    Renvoie le vecteur allant de src vers dst avec
    comme norme maximale norme
    """
    return (dst-src).norm_max(norme)

def get_oriented_angle(ref, other):
    """
    Renvoie l'angle oriente du vecteur ref vers
    le vecteur other, pourvu que les vecteurs
    soient unitaires
    """
    return asin(ref.x*other.y-ref.y*other.x)

def coeff_friction(n,fc):
    """
    Renvoie le coefficient d'une grandeur physique
    dont le taux de changement sur le temps varie
    de forme proportionnelle a fc
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

def shootPower(stateFoot, alphaShoot, betaShoot):
    """
    Renvoie la force avec laquelle on
    va frapper la balle selon la position
    de la balle (la distance et l'angle
    par rapport a l'horizontale)
    """
    vect = Vector2D(-1.,0.)
    u = stateFoot.opp_goal - stateFoot.my_pos
    dist = u.norm
    theta = acos(abs(vect.dot(u))/u.norm)/acos(0.)
    return maxPlayerShoot*(1.-exp(-(alphaShoot*dist)))*exp(-betaShoot*theta)

def passPower(stateFoot, dest, maxPower, thetaPass):
    """
    Renvoie la force avec laquelle on
    va faire une passer selon la distance
    de entre la balle et le recepteur
    """
    dist = dest.distance(stateFoot.ball_pos)
    return maxPower*(1.-exp(-(thetaPass*dist)))

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

def nearest_defender(stateFoot, liste, distRef):
    """
    Renvoie le defenseur adverse le plus proche dans un
    rayon de distRef en direction de la cage opposee,
    i.e. le joueur qui lui bloque la voie vers la cage
    """
    oppDef = None
    og = stateFoot.opp_goal
    dog = stateFoot.distance_ball(og)
    dist_min = distRef
    for j in liste:
        dist_j = stateFoot.distance_ball(j.position)
        if dist_j < dist_min and (j.position.distance(og) < dog or dist_j < 3.):
            oppDef = j
            dist_dmin = dist_j
    return oppDef
