# -*- coding: utf-8 -*-
from soccersimulator  import SoccerAction, Vector2D
from soccersimulator.settings import GAME_HEIGHT, GAME_WIDTH, GAME_GOAL_HEIGHT, \
    PLAYER_RADIUS, BALL_RADIUS, maxPlayerShoot
from math import acos, exp, asin, cos

## Classe enveloppe de notre super-etat du jeu
class Wrapper(object):
    def __init__(self, state):
        self._obj = state
    def __getattr__(self, attr):
        return getattr(self._obj,attr)


## StateFoot
#### C'est notre super-etat du jeu
#### Il nous facilite l'acces a certains aspects
#### de la configuration courante du terrain
#### depuis la perspective d'un joueur
class StateFoot(Wrapper):
    def __init__(self, state, id_team, id_player, numPlayers=1):
        super(StateFoot, self).__init__(state)
        self.key = (id_team, id_player)
        self.numPlayers = numPlayers
        self.ballsInside = [False] * len(state.balls)

    @property
    def nextBall(self):
        for i in range(len(self.ballsInside)):
            if not self.ballsInside[i]:
                return i
        return True

    @property
    def my_team(self):
        """
        L'identifiant de son equipe
        """
        return self.key[0]

    @property
    def opp_team(self):
        """
        L'identifiant de l'equipe adverse
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
        Son etat, i.e. sa position et vitesse
        """
        return self.player_state(*self.key)

    @property
    def my_pos(self):
        """
        Sa position instantanee
        """
        return self.my_state.position

    @property
    def my_speed(self):
        """
        Sa vitesse instantanee
        """
        return self.my_state.vitesse

    @property
    def ball_pos(self):
        """
        La position instantanee de la balle
        """
        return self.ball.position

    @property
    def ball_speed(self):
        """
        La vitesse instantanee de la balle
        """
        return self.ball.vitesse

    @property
    def my_goal(self):
        """
        La position du centre de sa cage
        """
        return Vector2D((self.my_team - 1) * self.width, self.goal_height)

    @property
    def opp_goal(self):
        """
        La position du centre de la cage adverse
        """
        return Vector2D((self.opp_team - 1) * self.width, self.goal_height)

    @property
    def poteau_sup(self):
        centre = self.opp_goal
        return centre + Vector2D(0., GAME_GOAL_HEIGHT/2.)

    @property
    def poteau_inf(self):
        centre = self.opp_goal
        return centre - Vector2D(0., GAME_GOAL_HEIGHT/2.)

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
    def attacking_vector(self):
        """
        Vecteur unitaire qui se dirige vers la cage adverse
        depuis sa propre cage
        """
        return (self.opp_goal - self.my_goal).normalize()

    @property
    def shoot_radius(self):
        """
        La distance maximum autorisee entre un joueur et la balle
        pour qu'il puisse la frapper
        """
        return PLAYER_RADIUS + BALL_RADIUS

    @property
    def shoot_precision(self):
        return 2 * BALL_RADIUS

    @property
    def teammates(self):
        """
        Ses coequipiers
        """
        team = self.my_team
        liste = [self.player_state(team,i) for i in range(self.nb_players(team))]
        liste.remove(self.my_state)
        return liste

    @property
    def offensive_teammates(self):
        """
        Ses coequipiers offensives (pour le 4v4)
        Hypothese : le CB est le premier joueur
        """
        team = self.teammates
        try:
            delete_teammate(self.player_state(self.my_team, 0), team)
        except:
            pass
        return team

    @property
    def opponents(self):
        """
        Ses adversaires
        """
        team = self.opp_team
        return [self.player_state(team,i) for i in range(self.nb_players(team))]

    def nearest_ball(self, liste):
        """
        Renvoie la position du joueur le plus proche de
        la balle parmi <liste>
        """
        return nearest_state(self.ball_pos, liste)

    @property
    def opponent_nearest_ball(self):
        """
        L'adversaire le plus proche de la balle
        """
        return self.nearest_ball(self.opponents)

    def nearest_opponent(self, rayPressing):
        """
        L'adversaire le plus proche du joueur
        dans un rayon <rayPressing>
        """
        opp = nearest_state(self.my_pos, self.opponents)
        if self.distance(opp.position) < rayPressing:
            return opp
        return None

    def opponent_1v1(self):
        """
        Son unique adversaire lorsqu'il s'agit d'un match 1v1
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

    def is_nearest_ball_aux(self, playersList):
        """
        Renvoie vrai ssi il est plus proche de 
        la balle que quiconque dans <playersList>
        """
        dist_ball_joueur = self.distance(self.ball_pos)
        for opp in playersList:
            if dist_ball_joueur >= self.distance_ball(opp.position):
                return False
        return True

    def is_nearest_ball(self):
        """
        Renvoie vrai ssi il est le joueur le plus proche
        de la balle
        """
        return self.is_nearest_ball_aux(self.opponents + self.teammates)

    def is_nearest_ball_my_team(self):
        """
        Renvoie vrai ssi il est le joueur de son equipe
        le plus proche de la balle
        """
        return self.is_nearest_ball_aux(self.teammates)

    def is_valid_position(self, pos):
        """
        Renvoie vrai ssi la position rentre dans le
        terrain de football
        """
        return pos.x >= 0. and pos.x < self.width \
            and pos.y >= 0. and pos.y < self.height

    def team_controls_ball(self):
        """
        Recherche d'abord le joueur le plus proche
        de la balle dans un rayon de 20 unites ;
        renvoie vrai si le joueur appartient a son
        equipe, faux s'il joue pour l'equipe adverse,
        et None s'il n'y en a pas
        """
        controler = self.nearest_ball([self.my_state] + self.teammates + self.opponents)
        if self.distance_ball(controler.position) < 20.:
            return not controler in self.opponents
        return None

    def free_trajectory(self, dest, angleInter):
        """
        Renvoie vrai ssi il n'y a pas d'adversaire
        dans un angle <angleInter> a partir du vecteur
        allant de la balle vers <dest>
        """
        vect = (dest - self.ball_pos).normalize()
        for opp in self.opponents:
            if dest.distance(opp.position) > self.distance_ball(dest):
                continue
            diff = opp.position-self.ball_pos
            if self.is_team_left():
                angle = get_oriented_angle(vect, diff.normalize())
            else:
                angle = get_oriented_angle(diff.normalize(), vect)
            if vect.y > 0.: angle = -angle
            if angle >= 0. and angle < angleInter:
                return False
        return True

    def free_pass_trajectory(self, tm, angleInter):
        """
        Renvoie vrai ssi aucun adversaire n'est
        susceptible d'intercepter la trajectoire d'une
        passe vers <tm>
        """
        return self.free_trajectory(tm.position, angleInter)



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
    Renvoie le vecteur allant de <src> vers <dst> avec
    comme norme maximale <norme>
    """
    return (dst-src).norm_max(norme)

def get_oriented_angle(ref, other):
    """
    Renvoie l'angle oriente du vecteur <ref> vers
    le vecteur <other>, pourvu que les vecteurs
    soient unitaires
    """
    return asin(ref.x*other.y-ref.y*other.x)

def coeff_friction(n,fc):
    """
    Renvoie le coefficient d'une grandeur physique
    dont le taux de changement sur le temps varie
    de forme proportionnelle a <fc>
    """
    return (1.-fc)*(1.-(1.-fc)**n)/fc

def is_in_radius_action(stateFoot, ref, distLimite):
    """
    Renvoie vrai ssi le point <ref> se trouve
    dans le cercle de rayon <distLimite> centre en la
    position de la balle
    """
    return ref.distance(stateFoot.ball_pos) <= distLimite

def distance_horizontale(v1, v2):
    """
    Renvoie la distance entre les abscisses de deux
    points
    """
    return abs(v1.x-v2.x)

def distance_verticale(v1, v2):
    """
    Renvoie la distance entre les ordonnees de deux
    points
    """
    return abs(v1.y-v2.y)

def is_upside(ref, other):
    """
    Renvoie vrai ssi <ref> est au-dessus de
    <other>
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
    return max(0.5,maxPlayerShoot*(1.-exp(-(alphaShoot*dist)))*exp(-betaShoot*theta))

def passPower(stateFoot, dest, maxPower, thetaPass):
    """
    Renvoie la force avec laquelle on
    va faire une passer selon la distance
    entre la balle et le recepteur
    """
    dist = stateFoot.distance_ball(dest)
    return maxPower*(1.-exp(-(thetaPass*dist)))

def nearest(ref, liste):
    """
    Renvoie la position du joueur le plus proche de
    <ref> parmi <liste>
    """
    p = nearest_state(ref, liste)
    if p is not None:
        return p.position
    return None

def nearest_state(ref, liste):
    """
    Renvoie l'etat du joueur le plus proche de
    <ref> parmi <liste>
    """
    p = None
    distMin = 1024.
    for o in liste:
        dist = ref.distance(o.position)
        if dist < distMin:
            p = o
            distMin = dist
    return p

def nearest_defender(stateFoot, liste, distRef):
    """
    Renvoie le defenseur adverse le plus proche dans un
    rayon de <distRef> en direction de la cage opposee,
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

def nearest_defender_def(stateFoot, liste, distRef):
    """
    Renvoie le defenseur adverse le plus proche dans un
    rayon de <distRef + 20.> en direction de la cage opposee,
    i.e. le joueur qui lui bloque la voie vers la cage
    """
    oppDef = None
    og = stateFoot.opp_goal
    dog = stateFoot.distance_ball(og)
    dist_min = distRef + 20.
    for j in liste:
        dist_j = stateFoot.distance_ball(j.position)
        if dist_j < dist_min and (j.position.distance(og) < dog or dist_j < 3.):
            vect = (stateFoot.ball_pos - j.position).normalize()
            speed = j.vitesse.copy().normalize()
            if dist_j > distRef and cos(get_oriented_angle(speed,vect)) < 0.88:
                continue
            oppDef = j
            dist_dmin = dist_j
    return oppDef

def delete_teammate(tm, liste):
    """
    Supprime <tm> de <liste>
    """
    index = -1
    for i in range(len(liste)):
        if liste[i].position == tm.position:
            index = i
            break
    liste.pop(index)
