# -*- coding: utf-8 -*-
from soccersimulator import Vector2D
from soccersimulator.settings import maxPlayerShoot
from .tools import is_in_radius_action
from .conditions import must_intercept, has_ball_control, is_defensive_zone, \
    is_close_goal, is_close_ball, opponent_approaches_my_goal, must_advance, \
    free_teammate, had_ball_control, is_kick_off, must_pass_ball, distance_horizontale, \
    both_must_kick, free_opponent, ball_advances, is_under_pressure
from .actions import goToBall, goToMyGoal, kickAt, shoot, control, dribble, passBall, \
    goForwardsDef, goForwardsPA, goForwardsMF, goForwardsDefSolo, goForwardsPASolo, \
    goForwardsMFSolo, mark, loseMark, clear, cutDownAngle, cutDownAngle_def, \
    cutDownAngle_gk, pushUp, tryInterception
    

def st_kickOffSolo(state, dico):
    """
    Comportement du fonceur lors du coup
    de sifflet
    """
    if has_ball_control(state):
        if both_must_kick(state) == 0:
            return goForwardsMF(state, dico)
        return shoot(state, 6.)
    return goToBall(state)

def st_kickOff(state, dico):
    """
    Comportement de l'attaquant lors du coup
    de sifflet
    """
    count = both_must_kick(state)
    if count > 1:
        return cutDownAngle_gk(state, 40.)
    if has_ball_control(state):
        if count == 1:
            return shoot(state, maxPlayerShoot)
        return control(state, dico['controleMT'])
    return goToBall(state)

def gk_kickOff(state, dico):
    """
    Comportement du gardien/defenseur lors du coup
    de sifflet
    """
    count = both_must_kick(state)
    if count != 1:
        return cutDownAngle_gk(state, 40.)
    if has_ball_control(state):
        return kickAt(state, Vector2D(state.opp_goal.x, 100.), maxPlayerShoot)
    return goToBall(state)

def WithBallControl_1v1(state, dico):
    """
    """
    if is_defensive_zone(state, dico['distDefZone']):
        return goForwardsDefSolo(state, dico)
    if is_close_goal(state, dico['distAttaque']):
        return goForwardsPASolo(state, dico)
    return goForwardsMFSolo(state, dico)

def WithoutBallControl_1v1(state, dico):
    """TODO
    Quand le joueur n'a pas le controle sur
    la balle:
    - si la balle approche il s'approche pour
    recevoir la balle
    - s'il est le joueur le plus proche de la
    balle ou s'il vient de faire un dribble/controle
    il se dirige de nouveau vers la balle
    - si un coequipier a franchi une distance
    avec la balle, il monte de le terrain
    pour lui proposer des solutions
    - sinon il se decale lateralement
    """
    if state.is_nearest_ball() or \
       had_ball_control(state, dico['rayReprise'], dico['angleReprise']):
        return tryInterception(state, dico)
    if must_intercept(state, dico['rayInter']):
        return tryInterception(state, dico)
    if not state.team_controls_ball():
        return tryInterception(state, dico)
    return cutDownAngle(state, dico['raySortie'], dico['rayInter'])

def WithBallControl_2v2(state, dico):
    """
    Le comportement d'un joueur d'une
    equipe a deux lorsqu'il controle
    la balle depend fortement de sa
    position sur le terrain : defense,
    milieu et attaque.
    """
    if is_defensive_zone(state, dico['distDefZone']):
        return goForwardsDef(state, dico)
    if is_close_goal(state, dico['distAttaque']):
        return goForwardsPA(state, dico)
    return goForwardsMF(state, dico)

def WithBallControl_4v4(state, dico):
    """
    Le comportement d'un joueur d'une
    equipe a quatre lorsqu'il controle
    la balle depend fortement de sa
    position sur le terrain : milieu
    et attaque.
    """
    if is_close_goal(state, dico['distAttaque']):
        return goForwardsPA(state, dico)
    return goForwardsMF(state, dico)

def WithoutBallControl_ST_2v4(state, dico):
    """TODO
    Quand le joueur n'a pas le controle sur
    la balle:
    - si la balle approche il s'approche pour
    recevoir la balle
    - s'il est le joueur le plus proche de la
    balle ou s'il vient de faire un dribble/controle
    il se dirige de nouveau vers la balle
    - si un coequipier a franchi une distance
    avec la balle, il monte de le terrain
    pour lui proposer des solutions
    - sinon il se decale lateralement
    """
    vectBall = (state.my_pos - state.ball_pos).normalize()
    vectSpeed = state.ball_speed.copy().normalize()
    if must_intercept(state, dico['rayRecept']) and vectSpeed.dot(vectBall) >= dico['angleRecept']:
        return tryInterception(state, dico)
    if state.is_nearest_ball() or \
       (had_ball_control(state, dico['rayReprise'], dico['angleReprise']) and state.is_nearest_ball_my_team()):
        return tryInterception(state, dico)
    if is_close_goal(state, dico['distAttaque']) and ball_advances(state) \
       and state.is_nearest_ball_my_team():
        return tryInterception(state, dico)
    if must_advance(state, dico['distMontee']):
        return pushUp(state, dico['coeffPushUp'])
    if state.is_nearest_ball_my_team() and must_intercept(state, dico['rayInter']):
        return tryInterception(state, dico)
    if state.numPlayers == 4:
        opp = free_opponent(state, dico['distDefZone'], dico['rayPressing'])
        if is_defensive_zone(state, dico['distDefZone']) and opp is not None:
            return mark(state, opp, dico['rayPressing'])
    if state.numPlayers == 2:
        opp = free_opponent(state, dico['distDefZone']+20., dico['rayPressing'])
        if opp is not None and not is_close_ball(state, opp.position):
            return mark(state, opp, dico['rayPressing'])
    if is_defensive_zone(state, dico['distDefZone']+20) and state.team_controls_ball():
        return loseMark(state, dico['rayPressing'], dico['distDemar'], dico['angleInter'])
    return cutDownAngle(state, dico['distShoot'], dico['rayInter'])

def WithoutBallControl_GK_2v4(state, dico):
    if state.is_nearest_ball() or \
       (had_ball_control(state, dico['rayReprise'], dico['angleReprise']) and state.is_nearest_ball_my_team()):
        return tryInterception(state, dico)
    if is_close_goal(state, dico['distAttaque']) and \
       ball_advances(state) and state.is_nearest_ball_my_team():
        return tryInterception(state, dico)
    if must_advance(state, dico['distMontee']):
        return pushUp(state, dico['coeffPushUp'])
    if must_intercept(state, dico['rayInter']):
        return tryInterception(state, dico)
    if state.distance_ball(state.my_goal) < 30.:
        return tryInterception(state, dico)
    if state.numPlayers == 2:
        raySortie = dico['raySortie']
    else: # state.numPlayers == 4
        raySortie = dico['distSortie']
    return cutDownAngle_def(state, raySortie, dico['rayInter'])

def WithBallControl_CBnaif(state, dico):
    tm = free_teammate(state, dico['angleInter'])
    if tm is not None and must_pass_ball(state, tm, dico['angleInter']) \
       and not is_under_pressure(state, tm, dico['rayPressing']):
        return passBall(state, tm, 2.*dico['powerPasse'], dico['thetaPasse'], dico['coeffPushUp']) + goToMyGoal(state)
    return clear(state) + goToMyGoal(state)
    
def WithoutBallControl_CBnaif_2v2(state, dico):
    if state.is_nearest_ball():
        return tryInterception(state, dico)
    if must_intercept(state, dico['rayInter']) and \
       is_in_radius_action(state, state.my_goal, dico['distSortie']):
        return tryInterception(state, dico)
    if state.distance_ball(state.my_goal) < 30.:
        return tryInterception(state, dico)
    return cutDownAngle_def(state, dico['raySortie'], dico['rayInter'])

def WithoutBallControl_CBnaif_4v4(state, dico):
    if state.is_nearest_ball():
        return tryInterception(state, dico)
    if must_intercept(state, dico['rayInter']) and is_in_radius_action(state, state.my_goal, dico['distSortie']) and state.is_nearest_ball_my_team():
        return tryInterception(state, dico)
    if state.distance_ball(state.my_goal) < dico['distDefZone']:
        return tryInterception(state, dico)
    return cutDownAngle_def(state, dico['raySortie'], dico['rayInter'])
